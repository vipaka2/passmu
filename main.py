import itertools
import random
import yaml # type: ignore

def load_config(filename='config.yaml'):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def normal_caps_variants(word):
    return {word.lower(), word.upper(), word.capitalize(), word.title()}

def random_caps(word):
    return ''.join(c.upper() if random.choice([True, False]) else c.lower() for c in word)

def insert_symbols_everywhere(word, symbols, max_symbols):
    positions = list(range(len(word) + 1))
    results = set([word])
    for n in range(1, max_symbols + 1):
        for sym_seq in itertools.product(symbols, repeat=n):
            for pos_seq in itertools.combinations_with_replacement(positions, n):
                chars = list(word)
                offset = 0
                for index, symbol in sorted(zip(pos_seq, sym_seq)):
                    chars.insert(index + offset, symbol)
                    offset += 1
                results.add(''.join(chars))
    return results

def leetspeak_realistic(word, leet_map, max_subs=2):
    indexes = [i for i, c in enumerate(word) if c.lower() in leet_map]
    variants = set([word])
    for subs in range(1, max_subs + 1):
        for pos_combo in itertools.combinations(indexes, subs):
            replacements = []
            for idx in pos_combo:
                c = word[idx].lower()
                replacements.append([(idx, rep) for rep in leet_map[c]])
            for reps in itertools.product(*replacements):
                chars = list(word)
                for idx, rep in reps:
                    chars[idx] = rep
                variants.add(''.join(chars))
    return variants

def filter_by_length(variants, min_len=8, max_len=None):
    return [
        pw for pw in variants
        if len(pw) >= min_len and (max_len is None or len(pw) <= max_len)
    ]

def generate_password_variants(base_word, config):
    base_words = normal_caps_variants(base_word)

    all_mutants = set()
    for form in base_words:
        mutated = insert_symbols_everywhere(
            form,
            config['symbols'],
            config['max_symbols']
        )
        all_mutants.update(mutated)

    random_caps_variants = set()
    for word in all_mutants:
        for _ in range(config['random_caps_per_variant']):
            random_caps_variants.add(random_caps(word))

    leet_variants = set()
    for word in all_mutants:
        leet_variants.update(
            leetspeak_realistic(
                word,
                config['real_world_leet'],
                max_subs=2
            )
        )

    full_set = all_mutants.union(random_caps_variants).union(leet_variants)

    return sorted(filter_by_length(
        full_set,
        min_len=config['min_password_length'],
        max_len=config['max_password_length']
    ))

def generate_name_combinations(name_input):
    parts = name_input.strip().split()
    if len(parts) != 2:
        return [name_input.strip()]
    first, last = parts
    combos = [
        first + last,
        first + '_' + last,
        first + '.' + last,
        first + '-' + last,
        last + first
    ]
    return combos

def main():
    config = load_config('config.yaml')
    min_len = config['min_password_length']
    max_len = config['max_password_length']

    print("🔐 Passmu (Password Mutation Generator)")
    base_word = input("Enter a base word: ").strip()
    if not base_word:
        print("❌ No input received. Exiting.")
        return

    if len(base_word) < min_len:
        print(f"⚠️  Base word '{base_word}' is shorter than {min_len} characters.")
    if len(base_word) > max_len:
        print(f"⚠️  Base word '{base_word}' is longer than {max_len} characters.")

    print(f"\n🔧 Generating mutations for: '{base_word}'")
    print(f"Symbols: {' '.join(config['symbols'])}")
    print(f"Max insertions: {config['max_symbols']}")
    print(f"Random caps per variant: {config['random_caps_per_variant']}")
    print(f"Leetspeak substitutions: enabled")

    all_variants = set()
    for word in generate_name_combinations(base_word):
        word_variants = generate_password_variants(word, config)
        all_variants.update(word_variants)

    variants = sorted(all_variants)

    print(f"\n✅ Generated {len(variants):,} password variants.")

    save = input("\n💾 Save output to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"{base_word.replace(' ', '_')}_mutations_.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for v in variants:
                f.write(v + '\n')
        print(f"✅ Saved to {filename}")

if __name__ == "__main__":
    main()
