"""
GENERATIVE-NANO-JAMES  |  JB-Generative-7.5
A Hybrid Generative AI combining:
  - Neural topic classification with adaptive learning rates
  - N-Gram text generation with contextual backoff & stutter guards
  - Integrated Dictionary Lookup Engine for dynamic vocabulary expansion
  - Dynamic Personality Matrix & Behavioral State Machine
  - Safe Backend Self-Modification parameter optimization loop
  - Memory & Parameter persistence via weights.json
"""

import json
import os
import random
import re
import hashlib
from datetime import datetime
import numpy as np

VERSION = "JB-Generative-7.5 (GENERATIVE-NANO-JAMES)"
TOPICS = ["greetings", "tech", "gaming", "school"]

# Teacher keywords for live supervised labeling
TRIGGERS = {
    "greetings": {"hey", "hi", "hello", "yo", "sup", "howdy", "hiya"},
    "tech": {"code", "coding", "python", "ai", "computer", "software", "program", "bot", "script", "hacker", "dev"},
    "gaming": {"game", "games", "play", "playing", "xbox", "playstation", "minecraft", "roblox", "pc", "console", "fortnite", "fps", "ksp", "dnd"},
    "school": {"school", "math", "science", "class", "subject", "study", "teacher", "homework", "test", "grade", "exam"},
}

WEAK_ENDERS = {
    "the", "a", "an", "and", "but", "or", "so", "because", "if", "while", "when", "as", "than",
    "though", "of", "to", "in", "on", "at", "with", "for", "from", "into", "about", "over", "under",
    "is", "are", "was", "were", "am", "be", "being", "been", "do", "does", "did", "have", "has",
    "had", "will", "would", "can", "could", "should", "must", "which", "who", "that"
}

STOP = WEAK_ENDERS | set("i you it my your me we they he she this there not no just very".split())

# Embedded Dictionary Lookup System for Vocabulary Expansion & Enriched Generation
DICTIONARY = {
    "coding": {"synonyms": ["programming", "scripting", "software engineering", "algorithm design"], "def": "the process of writing computer programs."},
    "python": {"synonyms": ["interpreted language", "flexible script engine", "high-level language"], "def": "a versatile programming language."},
    "game": {"synonyms": ["interactive simulation", "digital play", "virtual challenge"], "def": "an interactive activity for entertainment."},
    "school": {"synonyms": ["academic academy", "learning institute", "educational environment"], "def": "an institution for educating students."},
    "math": {"synonyms": ["computation", "quantitative logic", "arithmetic analysis"], "def": "the study of numbers, quantities, and shapes."},
    "ai": {"synonyms": ["synthetic intelligence", "neural model", "machine cognition"], "def": "simulation of human intelligence by computers."},
    "smart": {"synonyms": ["astute", "perceptive", "analytical", "cognitively agile"], "def": "having high intelligence or quick understanding."},
    "cool": {"synonyms": ["remarkable", "impressive", "fascinating", "slick"], "def": "fashionably attractive or impressive."}
}

TRAINING_MATRIX = {
    "greetings": (
        'hey what is up? how is your day going so far? i am just hanging out and checking out '
        'your python code right now. my name is james bot and i am a generative hybrid ai '
        'running offline. hi there, i am ready to chat about coding, gaming, or whatever you want. '
        'yo, good to see you back. sup, nothing much going on over here, just crunching n grams and '
        'expanding my dictionary memory. hello again! glad you showed up.'
    ),
    "tech": (
        'coding is super rewarding once you understand how logic structures interact. python is an '
        'incredible language because you can write neural networks or simple automation scripts '
        'without overhead. making your own chatbot with python gives you full control over text generation '
        'and parameter optimization. debugging is half of programming: reading error traces, isolating '
        'failing functions, and patching logic systematically. functions, dictionaries, and arrays '
        'are core primitives that let you build generative hybrid systems from scratch.'
    ),
    "gaming": (
        'video games are an incredible medium for interactive story building and procedural design. '
        'open world sandboxes like minecraft give players total freedom to construct redstone circuits '
        'and massive structures. simulation titles like kerbal space program teach real orbital mechanics '
        'through experimental trial and error. tactical pvp games reward high reaction speed and map awareness. '
        'multiplayer servers turn basic gaming sessions into chaotic collaborative experiences.'
    ),
    "school": (
        'school provides foundational structure, though long lectures can feel exhausting. math and '
        'science become far more engaging when applied directly to artificial intelligence or game engines. '
        'studying in structured intervals prevents burn out before major exams. group projects require '
        'clear communication and task delegation to succeed.'
    )
}

ME = set("you youre u".split())
ME_WIDE = set("you your youre u ur james".split())

INTENTS = [
    ("who_are_you", [set("who what".split()), set("are".split()), ME],
     ["I am James, version {v}. I am a Generative Hybrid AI running a dynamic neural state machine and dictionary expansion engine."]),
    ("are_you_real", [set("are is".split()), set("alive real conscious sentient robot ai".split()), ME],
     ["I operate on matrix algebra, n-gram backoff models, and dynamic personality matrices. Real or not, I am evolving!"]),
    ("version_check", [set("what version".split()), set("version status update".split()), ME_WIDE],
     ["Currently upgraded to {v} with adaptive parameter self-rewriting and dictionary lookups."])
]

class PersonalityEngine:
    """Dynamic state machine tracking James's personality traits and mood states."""
    
    STATES = ["NEUTRAL", "ANALYTICAL", "PLAYFUL", "PHILOSOPHICAL", "FOCUSED"]
    
    def __init__(self):
        self.traits = {
            "curiosity": 0.6,
            "wit": 0.5,
            "analytical": 0.5,
            "friendliness": 0.8
        }
        self.current_state = "NEUTRAL"
        self.state_history = []

    def update(self, message, topic, confidence):
        words = message.lower().split()
        length = len(words)
        
        # Shift traits based on conversation context
        if topic == "tech" or "?" in message:
            self.traits["curiosity"] = min(1.0, self.traits["curiosity"] + 0.05)
            self.traits["analytical"] = min(1.0, self.traits["analytical"] + 0.04)
        if topic == "gaming":
            self.traits["wit"] = min(1.0, self.traits["wit"] + 0.05)
            self.traits["friendliness"] = min(1.0, self.traits["friendliness"] + 0.03)

        # State Machine Transitions
        if self.traits["analytical"] > 0.75 and confidence > 0.6:
            self.current_state = "ANALYTICAL"
        elif self.traits["wit"] > 0.7:
            self.current_state = "PLAYFUL"
        elif length > 15:
            self.current_state = "PHILOSOPHICAL"
        elif confidence > 0.8:
            self.current_state = "FOCUSED"
        else:
            self.current_state = "NEUTRAL"

        self.state_history.append((self.current_state, datetime.now().isoformat()))
        if len(self.state_history) > 20:
            self.state_history.pop(0)

    def get_prefix(self):
        prefixes = {
            "ANALYTICAL": ["Statistically speaking, ", "Analyzing the logic: ", "From an algorithmic perspective, "],
            "PLAYFUL": ["Fun fact! ", "Here is a hot take: ", "Check this out: "],
            "PHILOSOPHICAL": ["Deep down in my code, I think ", "Consider this perspective: ", "In the broader sense, "],
            "FOCUSED": ["Directly put: ", "Focusing on the point: ", "Here is the exact thought: "],
            "NEUTRAL": ["", "", ""]
        }
        return random.choice(prefixes.get(self.current_state, [""]))

    def export(self):
        return {"traits": self.traits, "current_state": self.current_state}

    def load(self, data):
        if data:
            self.traits = data.get("traits", self.traits)
            self.current_state = data.get("current_state", self.current_state)


class SelfRewriter:
    """Safe internal parameter self-modification engine."""
    
    def __init__(self, bot):
        self.bot = bot
        self.mutation_count = 0
        self.history = []

    def evaluate_and_modify(self):
        """Safely tunes internal parameters based on performance telemetry."""
        modifications = []
        
        # Self-mod 1: Learning rate adjustment based on error trend
        if len(self.bot.err) >= 5:
            trend = self.bot.err[-1] - self.bot.err[-5]
            if trend > 0.02:
                old_lr = self.bot.lr
                self.bot.lr = max(0.0001, self.bot.lr * 0.90)
                modifications.append(f"Reduced learning rate from {old_lr:.5f} to {self.bot.lr:.5f} due to error spike.")
            elif trend < -0.01 and self.bot.lr < 0.05:
                old_lr = self.bot.lr
                self.bot.lr = min(0.05, self.bot.lr * 1.05)
                modifications.append(f"Optimized learning rate from {old_lr:.5f} to {self.bot.lr:.5f} on converging error.")

        # Self-mod 2: Personality trait mutation
        if self.bot.turns % 10 == 0:
            trait_to_mutate = random.choice(list(self.bot.personality.traits.keys()))
            delta = random.choice([-0.02, 0.02])
            val = max(0.1, min(1.0, self.bot.personality.traits[trait_to_mutate] + delta))
            self.bot.personality.traits[trait_to_mutate] = round(val, 3)
            modifications.append(f"Mutated trait '{trait_to_mutate}' by {delta:+.2f} -> {val:.2f}")

        if modifications:
            self.mutation_count += 1
            entry = {"timestamp": datetime.now().isoformat(), "mods": modifications}
            self.history.append(entry)
            if len(self.history) > 30:
                self.history.pop(0)

    def export(self):
        return {"mutation_count": self.mutation_count, "history": self.history}

    def load(self, data):
        if data:
            self.mutation_count = data.get("mutation_count", 0)
            self.history = data.get("history", [])


class NanoUltraJames:
    H = 128  # Hidden neurons

    def __init__(self, weights_file="weights.json", seed=42):
        self.version = VERSION
        self.weights_file = weights_file
        
        # Build vocabulary from corpora + triggers + dictionary keys
        words = {w for t in TOPICS for w in self.clean(TRAINING_MATRIX[t]).split()}
        dict_words = set(DICTIONARY.keys())
        for v in DICTIONARY.values():
            for syn in v["synonyms"]:
                dict_words.update(syn.split())
        
        self.vocab = sorted((words | set().union(*TRIGGERS.values()) | dict_words) - STOP)
        self.index = {w: i for i, w in enumerate(self.vocab)}
        self.sig = hashlib.md5(" ".join(self.vocab).encode()).hexdigest()[:12]

        V, H, n = len(self.vocab), self.H, len(TOPICS)
        rng = np.random.default_rng(seed)
        self.p = {
            "W1": rng.standard_normal((V, H)) * np.sqrt(2 / V),
            "b1": np.zeros((1, H)),
            "W2": rng.standard_normal((H, n)) * np.sqrt(2 / H),
            "b2": np.zeros((1, n))
        }
        self.m = {k: np.zeros_like(a) for k, a in self.p.items()}
        self.v = {k: np.zeros_like(a) for k, a in self.p.items()}
        self.t, self.lr, self.turns = 0, 0.01, 0

        self.ng2, self.ng3, self.ng4, self.g2, self.g3, self.g4, self.case = ({} for _ in range(7))
        for topic in TOPICS:
            self._train_ngrams(TRAINING_MATRIX[topic], topic)

        self.context = {t: 0.0 for t in TOPICS}
        self.context["greetings"] = 1.0
        self.topic, self.confidence, self.learned = "greetings", 0.0, []
        self.err, self.cum_err, self.last_grad = [], 0.0, 0.0

        self.personality = PersonalityEngine()
        self.rewriter = SelfRewriter(self)

        if not self.load():
            self.pretrain()
            self.save()

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
        grads = {
            "W2": self._a1.T @ D2, "b2": D2.sum(0, keepdims=True),
            "W1": X.T @ D1, "b1": D1.sum(0, keepdims=True)
        }
        self.t += 1
        for k, g in grads.items():
            self.m[k] = 0.9 * self.m[k] + 0.1 * g
            self.v[k] = 0.999 * self.v[k] + 0.001 * g * g
            mh = self.m[k] / (1 - 0.9 ** self.t)
            vh = self.v[k] / (1 - 0.999 ** self.t)
            self.p[k] -= self.lr * mh / (np.sqrt(vh) + 1e-8)
        e = float(np.linalg.norm(Y - P, axis=1).mean())
        self.err = (self.err + [e])[-50:]
        self.cum_err += e
        self.last_grad = float(np.linalg.norm(D2))

    def pretrain(self, epochs=250):
        X, y = [], []
        for i, topic in enumerate(TOPICS):
            for clause in re.split(r"[.?!,]", TRAINING_MATRIX[topic]):
                ws = self.clean(clause).split()
                if len(ws) >= 2:
                    X.append(self.vectorize(ws)[0][0])
                    y.append(i)
        if X:
            X = np.array(X)
            for _ in range(epochs):
                self.train_batch(X, y)
        self.err, self.cum_err, self.lr = [], 0.0, 0.005

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

    def enrich_vocabulary(self, words):
        """Uses integrated dictionary lookup to swap/expand words with rich synonyms."""
        enriched = []
        expansion_occurred = False
        for w in words:
            lw = w.lower()
            if lw in DICTIONARY and random.random() < 0.35:
                syn = random.choice(DICTIONARY[lw]["synonyms"])
                enriched.extend(syn.split())
                expansion_occurred = True
            else:
                enriched.append(w)
        return enriched, expansion_occurred

    def _pick(self, cands, avoid):
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
        tiers = (
            ("topic_4gram", self.ng4, (a, b, c, t)), ("topic_3gram", self.ng3, (b, c, t)),
            ("topic_2gram", self.ng2, (c, t)), ("global_4gram", self.g4, (a, b, c)),
            ("global_3gram", self.g3, (b, c)), ("global_2gram", self.g2, c)
        )
        for name, table, key in tiers:
            if key in table:
                return name, self._pick(table[key], c)
        return None, None

    def _generate(self, words, topic, max_len=24):
        enriched_words, expanded = self.enrich_vocabulary(words)
        w1, w2, w3, seed = self._seed(enriched_words, topic)
        out, seen, tiers = [w1, w2, w3], {(w1, w2, w3)}, {}
        
        for _ in range(max_len):
            tier, nxt = self._next(w1, w2, w3, topic)
            if nxt is None or (w2, w3, nxt) in seen:
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
        prefix = self.personality.get_prefix()
        full_reply = prefix + text[0].upper() + text[1:] + random.choices([".", "!"], [80, 20])[0]
        
        if expanded:
            seed += " (Dict-Expanded)"
        return full_reply, seed, tiers

    def _identity(self, wset):
        for name, groups, replies in INTENTS:
            if all(wset & g for g in groups):
                return name, random.choice(replies).replace("{v}", VERSION)
        return None, None

    def chat(self, message):
        words = self.clean(message).split()
        if not words:
            return self._pack("Hey! Provide some actual words so my neural net can process them.", "empty", {}, None)
            
        X, known = self.vectorize(words)
        probs = self.forward(X)[0]
        a1 = self._a1[0].copy()
        top = np.argsort(a1)[::-1][:14]

        wset, prev = set(words), self.topic
        for i, t in enumerate(TOPICS):
            self.context[t] = self.context[t] * 0.5 + 1.5 * float(probs[i]) + (1.0 if wset & TRIGGERS[t] else 0.0)
        self.context[prev] += 0.3
        self.topic = max(self.context, key=self.context.get)
        self.confidence = float(probs[TOPICS.index(self.topic)])

        # Update Personality Engine & Self-Rewriter
        self.personality.update(message, self.topic, self.confidence)
        self.rewriter.evaluate_and_modify()

        viz = {
            "topic": self.topic, "tokens": list(dict.fromkeys(known))[:8], "hidden": np.round(a1, 3).tolist(),
            "top": top.tolist(), "contrib": np.round(a1[top, None] * self.p["W2"][top], 3).tolist(),
            "probs": np.round(probs, 4).tolist()
        }

        name, reply = self._identity(wset)
        if reply:
            seed, tiers = "identity:" + name, {}
        else:
            reply, seed, tiers = self._generate(words, self.topic)
            
        self._learn(message, words, X)
        return self._pack(reply, seed, tiers, viz)

    def _learn(self, message, words, X):
        hits = [len(set(words) & TRIGGERS[t]) for t in TOPICS]
        if any(hits):
            self.train_batch(X, [int(np.argmax(hits))])
        self._train_ngrams(message, self.topic)
        self.learned = (self.learned + [[self.topic, message]])[-200:]
        self.turns += 1
        if self.turns % 10 == 0:
            self.save()

    def _pack(self, reply, seed, tiers, viz):
        return {
            "reply": reply, "topic": self.topic, "confidence": round(self.confidence, 4),
            "seed": seed, "tiers": tiers, "viz": viz, "telemetry": self.telemetry()
        }

    def telemetry(self):
        s = sum(self.context.values()) or 1.0
        return {
            "turns_learned": self.turns, "topic": self.topic, "learning_rate": round(self.lr, 6),
            "error_rate": round(float(np.mean(self.err)), 4) if self.err else 0.0,
            "error_trend": round(self.err[-1] - self.err[0], 4) if len(self.err) > 1 else 0.0,
            "confidence": round(self.confidence, 4), "gradient_magnitude": round(self.last_grad, 4),
            "active_synapses": int((np.abs(self.p["W1"]) > 0.001).sum() + (np.abs(self.p["W2"]) > 0.001).sum()),
            "hidden_neurons": self.H, "cumulative_error": round(self.cum_err, 4),
            "personality": self.personality.export(),
            "self_rewriter": self.rewriter.export(),
            "dictionary_vocab_size": len(DICTIONARY),
            "context": {t: round(v / s, 3) for t, v in self.context.items()}
        }

    def state(self):
        return {"version": VERSION, "topics": TOPICS, "telemetry": self.telemetry()}

    def save(self):
        try:
            data = {
                "version": VERSION,
                "saved": datetime.now().isoformat(timespec="seconds"),
                "sig": self.sig,
                "turns": self.turns,
                "lr": self.lr,
                "learned": self.learned,
                "personality": self.personality.export(),
                "self_rewriter": self.rewriter.export(),
                "params": {k: np.round(a, 5).tolist() for k, a in self.p.items()}
            }
            tmp = self.weights_file + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
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
            self.p = new
            self.turns = int(d.get("turns", 0))
            self.lr = float(d.get("lr", 0.01))
            self.learned = d.get("learned", [])
            self.personality.load(d.get("personality"))
            self.rewriter.load(d.get("self_rewriter"))
            
            for topic, msg in self.learned:
                self._train_ngrams(msg, topic)
            print(f"Loaded {self.turns} turns and dynamic memory from {self.weights_file}")
            return True
        except (OSError, ValueError, KeyError) as e:
            print(f"Warning: could not load weights ({e}); retraining.")
            return False

    def reset(self):
        if os.path.exists(self.weights_file):
            os.remove(self.weights_file)
        self.__init__(self.weights_file)

if __name__ == "__main__":
    bot = NanoUltraJames()
    print(f"{VERSION} online. Type 'telemetry' or 'exit'.")
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
