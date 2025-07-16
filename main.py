import itertools
import random

DEFAULT_SYMBOLS = ['!', '@', '#', '$', '%', '&', '*', '?', '1', '2', '3']
DEFAULT_MAX_SYMBOLS = 3
DEFAULT_RANDOM_CAPS_PER_VARIANT = 2

REAL_WORLD_LEET = {
    'a': ['@', '4'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['$', '5'],
    't': ['7'],
    'l': ['1'],
}

def normal_caps_variants(word):
    """Generate common capitalization styles."""
    return {
        word.lower(),
        word.upper(),
        word.capitalize(),
        word.title(),
    }

def random_caps(word):
    """Generate one randomly capitalized variant of a word."""
    return ''.join(c.upper() if random.choice([True, False]) else c.lower() for c in word)

def insert_symbols_everywhere(word, symbols, max_symbols=3):
    """Insert up to max_symbols into the word at all positions."""
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

def leetspeak_realistic(word, max_subs=2):
    """Generate leetspeak variants by applying up to max_subs."""
    indexes = [i for i, c in enumerate(word) if c.lower() in REAL_WORLD_LEET]
    variants = set([word])
    for subs in range(1, max_subs + 1):
        for pos_combo in itertools.combinations(indexes, subs):
            replacements = []
            for idx in pos_combo:
                c = word[idx].lower()
                replacements.append([(idx, rep) for rep in REAL_WORLD_LEET[c]])
            for reps in itertools.product(*replacements):
                chars = list(word)
                for idx, rep in reps:
                    chars[idx] = rep
                variants.add(''.join(chars))
    return variants

def generate_password_variants(base_word):
    # 1. Generate common capitalization forms
    base_words = normal_caps_variants(base_word)

    # 2. Insert symbols/numbers into all base forms
    all_mutants = set()
    for form in base_words:
        mutated = insert_symbols_everywhere(form, DEFAULT_SYMBOLS, DEFAULT_MAX_SYMBOLS)
        all_mutants.update(mutated)

    # 3. Add random capitalization
    random_caps_variants = set()
    for word in all_mutants:
        for _ in range(DEFAULT_RANDOM_CAPS_PER_VARIANT):
            random_caps_variants.add(random_caps(word))

    # 4. Apply leetspeak to all mutated forms
    leet_variants = set()
    for word in all_mutants:
        leet_variants.update(leetspeak_realistic(word, max_subs=2))

    final_set = sorted(all_mutants.union(random_caps_variants).union(leet_variants))
    return final_set

def main():
    print("🔐 Passmu (Password Mutation Generator)")
    base_word = input("Enter a base word (e.g. 'password'): ").strip()
    if not base_word:
        print("❌ You must enter a base word.")
        return

    print(f"\n🔧 Generating mutations for: '{base_word}'")
    print(f"Symbols used: {' '.join(DEFAULT_SYMBOLS)}")
    print(f"Max symbols inserted: {DEFAULT_MAX_SYMBOLS}")
    print(f"Random caps per variant: {DEFAULT_RANDOM_CAPS_PER_VARIANT}")
    print(f"Leetspeak style: Realistic, using common patterns")

    variants = generate_password_variants(base_word)

    print(f"\n✅ Generated {len(variants):,} password variants.")

    save = input("\n💾 Save output to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"{base_word}_mutations_full_leet.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for v in variants:
                f.write(v + '\n')
        print(f"✅ Saved to {filename}")

if __name__ == "__main__":
    main()
