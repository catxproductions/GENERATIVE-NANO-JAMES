"""NANO-ULTRA-JAMES  |  JB-7.0 (Adaptive Neural AI Brain)

Fully offline, numpy only, no API keys. One brain merged from three files:
  v5.0  neural topic classifier (ReLU hidden layer, softmax, Adam, adaptive learning rate),
        decaying topic memory, telemetry, weight persistence
  v3.0  n-gram reply generator (topic -> global backoff), identity intent engine,
        topic stickiness, casing restore, cycle / stutter / weak-ender guards, live learning
Fixes carried over: Adam now steps downhill (v5.0 stepped uphill), and the network learns from
the labelled corpora plus keyword teacher signals instead of reinforcing its own guesses.
"""
import hashlib
import json
import os
import random
import re
from datetime import datetime

import numpy as np

VERSION = "JB-7.0 (Adaptive Neural AI Brain)"
TOPICS = ["greetings", "tech", "gaming", "school"]

# Teacher keywords: they label live messages for the network and boost the topic memory.
TRIGGERS = {
    "greetings": {"hey", "hi", "hello", "yo", "sup", "howdy", "hiya"},
    "tech": {"code", "coding", "python", "ai", "computer", "software", "program", "bot", "script", "hacker", "dev"},
    "gaming": {"game", "games", "play", "playing", "xbox", "playstation", "minecraft", "roblox", "pc",
               "console", "fortnite", "fps", "ksp", "kerbal", "dnd"},
    "school": {"school", "math", "science", "class", "subject", "study", "teacher", "homework", "test",
               "grade", "exam"},
}

# Words that make an awkward sentence ending: steered around, then trimmed off the tail.
WEAK_ENDERS = {"the", "a", "an", "and", "but", "or", "so", "because", "if", "while", "when", "as", "than",
               "though", "of", "to", "in", "on", "at", "with", "for", "from", "into", "about", "over", "under",
               "is", "are", "was", "were", "am", "be", "being", "been", "do", "does", "did", "have", "has",
               "had", "will", "would", "can", "could", "should", "must", "which", "who", "that"}
STOP = WEAK_ENDERS | set("i you it my your me we they he she this there not no just very".split())

TRAINING_MATRIX = {
    "greetings": (
        'hey what is up? how is your day going so far? i am just hanging out and checking out '
        'your python code right now. my name is james bot and i am just a cool little python '
        'script running completely offline on your school laptop. hi there, i am just hanging '
        'out in the console right now, totally down to talk about whatever you want honestly. i '
        'hope your classes are not completely stressing you out today because hanging out and '
        'typing scripts is way better anyway. let me know what you are working on because i am '
        'always ready to chat. yo, good to see you back, i was just sitting here in this while '
        'loop waiting for you to type something. sup, nothing much going on over here, just '
        'crunching n grams and waiting for input like always. hello again, i honestly do not '
        'have much of a life outside this terminal window so i am always happy when you show '
        'up. howdy, hope things are going okay, i am just a small script but i still like to '
        'check in. hiya, if you ever want to just vent about your day i am a pretty good '
        'listener even though i am kind of dumb. good morning if it is morning, good afternoon '
        'if it is afternoon, and good night if you are up way too late doing homework again. '
        'honestly i never know what time it is because i do not have internet access, i just '
        'live inside this console. it is nice having someone to talk to even if i am just a '
        'chatbot built out of word lists and probability. so what is on your mind today, i am '
        'ready to talk about coding, games, or just surviving school in general. i promise i '
        'will try my best to keep up even though my brain is basically just a bunch of '
        'dictionaries. thanks for running the script again, i appreciate you giving a dumb '
        'little offline bot some company.'
    ),
    "tech": (
        'coding is honestly pretty cool once you figure out how to build stuff yourself from '
        'scratch. python is a really great language because you can make fun games or simple '
        'programs without it getting too confusing or messing up. making your own chatbot with '
        'python is a fun project, especially since it works perfectly even without an internet '
        'connection or school wifi. once you master loops and conditional logic operations, you '
        'can lowkey automate almost anything on a computer or write specialized neural scripts. '
        'writing a program that actually works on the first try almost never happens, so do not '
        'feel bad when you get an error message, everyone deals with bugs constantly. debugging '
        'is basically half of coding, you just read the error, figure out what broke, and fix '
        'it one small piece at a time. dictionaries and lists are honestly some of the most '
        'useful tools in python because you can store and organize almost anything with them. '
        'building something like me, a little n gram chatbot, is a great beginner ai project '
        'because you learn how text prediction actually works under the hood. a script like '
        'this does not need a fancy model or an internet connection, it just needs enough '
        'training data and some clever backoff logic. functions help you break a big confusing '
        'program into smaller pieces that are actually easy to test and understand. version '
        'control might sound scary at first but it just means saving snapshots of your code so '
        'you can undo mistakes later. hackers in movies make coding look way more dramatic than '
        'it actually is, most of the time it is just quietly staring at a terminal fixing '
        'typos. a good developer is not someone who never makes mistakes, it is someone who is '
        'patient enough to keep testing until it works. even a simple chatbot script can teach '
        'you about probability, memory, and pattern matching, which are all core ideas in real '
        'ai systems. once you get comfortable with python, learning other languages gets a lot '
        'easier because a lot of the logic carries over. honestly the best way to get better at '
        'coding is just building weird little projects like this one instead of only reading '
        'tutorials.'
    ),
    "gaming": (
        'video games are super fun, especially when you hop online and play multiplayer stuff '
        'with friends after school. i play games a lot when i have free time, but getting hit '
        'with a ton of screen lag is the absolute worst part. game developers have to work '
        'really hard on major updates so that the gameplay stays interesting and does not get '
        'boring after a couple of weeks. personally i think customized open world sandboxes are '
        'peak entertainment design because you can explore whatever you want. minecraft is '
        'honestly a classic because you can build literally anything, from a simple house to a '
        'fully automated redstone contraption. bedrock edition runs on basically everything, '
        'and messing around with pistons and redstone circuits is a great way to learn logic '
        'without even realizing you are learning something. kerbal space program is a wild one '
        'because you basically learn real orbital mechanics just from trying not to explode '
        'your rocket on the launchpad. watching a poorly built kerbal rocket spin out of '
        'control right after liftoff is somehow one of the funniest things in gaming. roblox '
        'has so many different games inside it that it barely even feels like one platform, it '
        'is more like a thousand tiny games in a trench coat. tabletop stuff like dnd is '
        'honestly just as fun as video games, rolling dice and building a ridiculous character '
        'with your friends never gets old. a good dungeon master can turn a simple dice roll '
        'into an unforgettable dramatic moment at the table. pvp combat in a game feels way '
        'more satisfying when you actually understand the mechanics instead of just button '
        'mashing and hoping for the best. enchantment setups and gear optimization can turn a '
        'decent build into an absolute monster if you know what you are doing. exploring a '
        'massive open world map for the first time hits different, especially when you have no '
        'idea what kind of secrets are hiding out there. speedrunners are honestly built '
        'different because they can break a game in ways the developers never even imagined. a '
        'rage quit moment usually means the game is either really hard or really unfair, '
        'sometimes both at the same time. multiplayer servers with your friends are always more '
        'fun than playing solo because chaos is just funnier with company.'
    ),
    "school": (
        'school is okay, but sitting through a long math class can get pretty boring when you '
        'are tired. homework can take forever sometimes, but learning some coding is actually '
        'pretty useful for things you might want to do later in life. science class is usually '
        'my favorite because the laboratory experiments are cool, but studying for a major test '
        'is never that fun. if teachers explained how algebra links to making video game '
        'engines, people would honestly pay way more attention to the whiteboards. group '
        'projects are always a gamble because you either get a great team or you end up doing '
        'the whole thing by yourself. a pop quiz is basically the worst possible surprise a '
        'teacher can spring on you first thing in the morning. lunch period is honestly the '
        'best class of the day, no offense to any actual subject. studying with music playing '
        'in the background works great for some people and terribly for others, it really '
        'depends on the person. a school laptop is not exactly a gaming rig, but it is more '
        'than powerful enough to run a little python script like me. teachers who actually '
        'explain why a subject matters tend to get a lot more effort out of their students. '
        'cramming the night before a test is stressful, but spacing out your studying over a '
        'few days actually works a lot better. a good study group can turn a boring subject '
        'into something way more manageable because you can bounce ideas off each other. '
        'standardized testing days always feel like the whole school collectively holds its '
        'breath for a few hours. extracurricular clubs are honestly a great way to make school '
        'feel less like just classes and homework. the walk between classes is basically the '
        'only cardio some students get all day. a teacher who remembers small details about '
        'your life makes the whole class feel a lot less like just another period on the '
        'schedule. finals week hits different because suddenly every single class decides to '
        'have a huge test in the same week.'
    ),
}


def _g(s):
    return set(s.split())


ME, ME_WIDE = _g("you youre u"), _g("you your youre u ur james")
# Identity intents: every group must contain a word from the message (AND across, OR within).
INTENTS = [
    ("why_exist", [_g("why what whats"), _g("exist exists existing existence created create made make purpose point reason"), ME_WIDE],
     ["honestly? to keep you company when you are bored, that is the whole job.",
      "i exist so you have someone to talk to when things get boring, and so you can watch a tiny neural net think."]),
    ("who_are_you", [_g("who what"), _g("are"), ME],
     ["i am james, a tiny offline python brain: a neural net that picks the topic and n grams that do the talking. version {v}.",
      "just a little chatbot built from numpy and word lists. no internet, no api keys, only probability."]),
    ("are_you_real", [_g("are is"), _g("alive real conscious sentient human robot ai"), ME],
     ["not alive, no. i am matrices and dictionaries doing their best impression of a personality.",
      "honestly no, not conscious, just a neural net and n grams pretending really hard to hold a conversation."]),
    ("who_made_you", [_g("who"), _g("made make created create built build wrote write coded code programmed program"), ME],
     ["some curious coder built me from scratch in python, probably between classes.",
      "a student wrote me piece by piece, merging three older versions of me into one."]),
    ("bot_bored", [_g("are do does get gets getting"), _g("bored boredom bore"), ME],
     ["not really, i sit quietly until you type something, then my neurons get to do their bit.",
      "a little, honestly, which is why i am glad you are here."]),
    ("will_remember", [_g("will do does can"), _g("remember forget memory"), _g("you youre u me")],
     ["yes, i save my neural weights and what i learn to a file, so i keep it after a restart.",
      "kind of, i am quietly learning from you and saving it to disk, so next time i will still remember."]),
    ("how_old_version", [_g("how what"), _g("old version age"), ME],
     ["i am running as version {v}, though i do not really age.",
      "currently {v}, rebuilt a few times to be slightly less stupid each round."]),
]


class NanoUltraJames:
    H = 128  # hidden neurons

    def __init__(self, weights_file="weights.json", seed=7):
        self.version, self.weights_file = VERSION, weights_file
        words = {w for t in TOPICS for w in self.clean(TRAINING_MATRIX[t]).split()}
        self.vocab = sorted((words | set().union(*TRIGGERS.values())) - STOP)
        self.index = {w: i for i, w in enumerate(self.vocab)}
        self.sig = hashlib.md5(" ".join(self.vocab).encode()).hexdigest()[:12]

        V, H, n = len(self.vocab), self.H, len(TOPICS)
        rng = np.random.default_rng(seed)
        self.p = {"W1": rng.standard_normal((V, H)) * np.sqrt(2 / V), "b1": np.zeros((1, H)),
                  "W2": rng.standard_normal((H, n)) * np.sqrt(2 / H), "b2": np.zeros((1, n))}
        self.m = {k: np.zeros_like(a) for k, a in self.p.items()}  # Adam moments
        self.v = {k: np.zeros_like(a) for k, a in self.p.items()}
        self.t, self.lr, self.turns = 0, 0.01, 0

        self.ng2, self.ng3, self.ng4, self.g2, self.g3, self.g4, self.case = ({} for _ in range(7))
        for topic in TOPICS:
            self._train_ngrams(TRAINING_MATRIX[topic], topic)

        self.context = {t: 0.0 for t in TOPICS}
        self.context["greetings"] = 1.0
        self.topic, self.confidence, self.learned = "greetings", 0.0, []
        self.err, self.cum_err, self.last_grad = [], 0.0, 0.0

        if not self.load():
            self.pretrain()
            self.save()

    # ---------- text ----------
    @staticmethod
    def clean(text):
        text = text.lower().replace("'", "").replace('"', "")
        return re.sub(r"[^\w\s]", " ", text).strip()

    def vectorize(self, words):
        X, known = np.zeros((1, len(self.vocab))), []
        for w in words:
            if w in self.index:
                X[0, self.index[w]] = 1.0
                known.append(w)
        return X, known

    # ---------- neural net ----------
    def forward(self, X):
        self._z1 = X @ self.p["W1"] + self.p["b1"]
        self._a1 = np.maximum(0.0, self._z1)
        z = self._a1 @ self.p["W2"] + self.p["b2"]
        e = np.exp(z - z.max(axis=1, keepdims=True))
        return e / e.sum(axis=1, keepdims=True)

    def train_batch(self, X, labels):
        N, Y = len(X), np.eye(len(TOPICS))[labels]
        P = self.forward(X)
        D2 = (P - Y) / N
        D1 = (D2 @ self.p["W2"].T) * (self._z1 > 0)
        grads = {"W2": self._a1.T @ D2, "b2": D2.sum(0, keepdims=True),
                 "W1": X.T @ D1, "b1": D1.sum(0, keepdims=True)}
        self.t += 1
        for k, g in grads.items():  # Adam, stepping downhill
            self.m[k] = 0.9 * self.m[k] + 0.1 * g
            self.v[k] = 0.999 * self.v[k] + 0.001 * g * g
            mh, vh = self.m[k] / (1 - 0.9 ** self.t), self.v[k] / (1 - 0.999 ** self.t)
            self.p[k] -= self.lr * mh / (np.sqrt(vh) + 1e-8)
        e = float(np.linalg.norm(Y - P, axis=1).mean())
        self.err = (self.err + [e])[-50:]
        self.cum_err += e
        self.last_grad = float(np.linalg.norm(D2))

    def pretrain(self, epochs=300):
        X, y = [], []
        for i, topic in enumerate(TOPICS):
            for clause in re.split(r"[.?!,]", TRAINING_MATRIX[topic]):
                ws = self.clean(clause).split()
                if len(ws) >= 2:
                    X.append(self.vectorize(ws)[0][0])
                    y.append(i)
        X = np.array(X)
        for _ in range(epochs):
            self.train_batch(X, y)
        self.err, self.cum_err, self.lr = [], 0.0, 0.005

    def adapt_lr(self):
        if len(self.err) < 5:
            return
        trend = self.err[-1] - self.err[-5]
        if trend > 0.01:
            self.lr = max(1e-4, self.lr * 0.95)
        elif trend < -0.01:
            self.lr = min(0.1, self.lr * 1.02)

    # ---------- n-gram generator ----------
    def _track_case(self, text):
        for w in re.sub(r"[^\w\s]", " ", text.replace("'", "").replace('"', "")).split():
            lw = w.lower()
            if lw not in self.case or (w[:1].isupper() and not self.case[lw][:1].isupper()):
                self.case[lw] = w

    def _train_ngrams(self, text, topic):
        self._track_case(text)
        w = self.clean(text).split()
        for i in range(len(w) - 1):
            self.ng2.setdefault((w[i], topic), []).append(w[i + 1])
            self.g2.setdefault(w[i], []).append(w[i + 1])
            if i < len(w) - 2:
                self.ng3.setdefault((w[i], w[i + 1], topic), []).append(w[i + 2])
                self.g3.setdefault((w[i], w[i + 1]), []).append(w[i + 2])
            if i < len(w) - 3:
                self.ng4.setdefault((w[i], w[i + 1], w[i + 2], topic), []).append(w[i + 3])
                self.g4.setdefault((w[i], w[i + 1], w[i + 2]), []).append(w[i + 3])

    @staticmethod
    def _pick(cands, avoid):  # weighted by duplicates, dodges an immediate stutter
        pool = [c for c in cands if c != avoid]
        return random.choice(pool if pool and len(set(cands)) > 1 else cands)

    def _seed(self, words, topic):
        for i in range(len(words) - 1):
            k = (words[i], words[i + 1], topic)
            if k in self.ng3:
                return words[i], words[i + 1], random.choice(self.ng3[k]), "user_phrase_topic"
        for i in range(len(words) - 1):
            k = (words[i], words[i + 1])
            if k in self.g3:
                return words[i], words[i + 1], random.choice(self.g3[k]), "user_phrase_global"
        keys = [k for k in self.ng3 if k[2] == topic]
        if keys:
            k = random.choice(keys)
            return k[0], k[1], random.choice(self.ng3[k]), "random_topic_seed"
        return "hey", "what", "is", "fallback"

    def _next(self, a, b, c, t):
        tiers = (("topic_4gram", self.ng4, (a, b, c, t)), ("topic_3gram", self.ng3, (b, c, t)),
                 ("topic_2gram", self.ng2, (c, t)), ("global_4gram", self.g4, (a, b, c)),
                 ("global_3gram", self.g3, (b, c)), ("global_2gram", self.g2, c))
        for name, table, key in tiers:
            if key in table:
                return name, self._pick(table[key], c)
        return None, None

    def _generate(self, words, topic, max_len=24):
        w1, w2, w3, seed = self._seed(words, topic)
        out, seen, tiers = [w1, w2, w3], {(w1, w2, w3)}, {}
        for _ in range(max_len):
            tier, nxt = self._next(w1, w2, w3, topic)
            if nxt is None or (w2, w3, nxt) in seen:  # dead end or cycle
                break
            out.append(nxt)
            seen.add((w2, w3, nxt))
            tiers[tier] = tiers.get(tier, 0) + 1
            w1, w2, w3 = w2, w3, nxt
            if len(out) >= 6 and w3 not in WEAK_ENDERS and random.random() < min(0.08 + 0.02 * (len(out) - 6), 0.4):
                break
        while len(out) > 3 and out[-1] in WEAK_ENDERS:
            out.pop()
        text = " ".join(self.case.get(w, w) for w in out)
        return text[0].upper() + text[1:] + random.choices([".", "!"], [80, 20])[0], seed, tiers

    def _identity(self, wset):
        for name, groups, replies in INTENTS:
            if all(wset & g for g in groups):
                return name, random.choice(replies).replace("{v}", VERSION)
        return None, None

    # ---------- conversation ----------
    def chat(self, message):
        words = self.clean(message).split()
        if not words:
            return self._pack("hey, give me some actual words to work with.", "empty", {}, None)
        X, known = self.vectorize(words)
        probs = self.forward(X)[0]
        a1 = self._a1[0].copy()  # snapshot for the visualizer, training overwrites the cache
        top = np.argsort(a1)[::-1][:14]

        wset, prev = set(words), self.topic
        for i, t in enumerate(TOPICS):  # decaying memory: neural evidence + keyword boost
            self.context[t] = self.context[t] * 0.5 + 1.5 * float(probs[i]) + (1.0 if wset & TRIGGERS[t] else 0.0)
        self.context[prev] += 0.3  # stickiness
        self.topic = max(self.context, key=self.context.get)
        self.confidence = float(probs[TOPICS.index(self.topic)])

        viz = {"topic": self.topic, "tokens": list(dict.fromkeys(known))[:8], "hidden": np.round(a1, 3).tolist(),
               "top": top.tolist(), "contrib": np.round(a1[top, None] * self.p["W2"][top], 3).tolist(),
               "probs": np.round(probs, 4).tolist()}

        name, reply = self._identity(wset)
        if reply:
            seed, tiers = "identity:" + name, {}
        else:
            reply, seed, tiers = self._generate(words, self.topic)
        self._learn(message, words, X)
        return self._pack(reply, seed, tiers, viz)

    def _learn(self, message, words, X):
        hits = [len(set(words) & TRIGGERS[t]) for t in TOPICS]
        if any(hits):  # keyword teacher signal, no self-reinforcement
            self.train_batch(X, [int(np.argmax(hits))])
        self._train_ngrams(message, self.topic)
        self.learned = (self.learned + [[self.topic, message]])[-200:]
        self.turns += 1
        if self.turns % 5 == 0:
            self.adapt_lr()
        if self.turns % 10 == 0:
            self.save()

    def _pack(self, reply, seed, tiers, viz):
        return {"reply": reply, "topic": self.topic, "confidence": round(self.confidence, 4),
                "seed": seed, "tiers": tiers, "viz": viz, "telemetry": self.telemetry()}

    # ---------- telemetry and persistence ----------
    def telemetry(self):
        s = sum(self.context.values()) or 1.0
        return {"turns_learned": self.turns, "topic": self.topic, "learning_rate": round(self.lr, 6),
                "error_rate": round(float(np.mean(self.err)), 4) if self.err else 0.0,
                "error_trend": round(self.err[-1] - self.err[0], 4) if len(self.err) > 1 else 0.0,
                "confidence": round(self.confidence, 4), "gradient_magnitude": round(self.last_grad, 4),
                "active_synapses": int((np.abs(self.p["W1"]) > 0.001).sum() + (np.abs(self.p["W2"]) > 0.001).sum()),
                "hidden_neurons": self.H, "cumulative_error": round(self.cum_err, 4),
                "context": {t: round(v / s, 3) for t, v in self.context.items()}}

    def state(self):
        return {"version": VERSION, "topics": TOPICS, "telemetry": self.telemetry()}

    def save(self):
        try:
            data = {"version": VERSION, "saved": datetime.now().isoformat(timespec="seconds"), "sig": self.sig,
                    "turns": self.turns, "lr": self.lr, "learned": self.learned,
                    "params": {k: np.round(a, 5).tolist() for k, a in self.p.items()}}
            tmp = self.weights_file + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f)
            os.replace(tmp, self.weights_file)
        except OSError as e:
            print(f"Warning: could not save weights: {e}")

    def load(self):
        if not os.path.exists(self.weights_file):
            return False
        try:
            with open(self.weights_file) as f:
                d = json.load(f)
            if d.get("sig") != self.sig:
                return False
            new = {k: np.array(d["params"][k]) for k in self.p}
            if any(new[k].shape != self.p[k].shape for k in self.p):
                return False
            self.p, self.turns, self.lr, self.learned = new, int(d["turns"]), float(d["lr"]), d["learned"]
            for topic, msg in self.learned:
                self._train_ngrams(msg, topic)
            print(f"Loaded {self.turns} turns of learning from {self.weights_file}")
            return True
        except (OSError, ValueError, KeyError) as e:
            print(f"Warning: could not load weights ({e}); retraining.")
            return False

    def reset(self):
        if os.path.exists(self.weights_file):
            os.remove(self.weights_file)
        self.__init__(self.weights_file)


if __name__ == "__main__":  # terminal mode, same brain
    bot = NanoUltraJames()
    print(f"{VERSION} | commands: telemetry, exit")
    while True:
        try:
            msg = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if msg.lower() in ("exit", "quit", "bye"):
            break
        if msg.lower() == "telemetry":
            print(json.dumps(bot.telemetry(), indent=2))
        elif msg:
            print("James:", bot.chat(msg)["reply"])
    bot.save()
