import multiprocessing
import itertools
import argparse
import random
import yaml  # type: ignore
import time
import gzip

def load_config(filename='config.yaml'):
    with open(filename, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_names(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            first_names = data.get('first_names', [])
            last_names = data.get('last_names', [])
            return list(first_names), list(last_names)
    except FileNotFoundError:
        print(f"[!] Unable to find {filename}.")
        return [], []

def normal_caps_variants(word):
    word = str(word)
    return {word.lower(), word.upper(), word.capitalize(), word.title()}

def random_caps(word):
    return ''.join(c.upper() if random.choice([True, False]) else c.lower() for c in word)

def insert_symbols_everywhere(word, symbols, max_symbols):
    if not symbols:
        return {word}
    positions = list(range(len(word) + 1))
    results = {word}

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
    variants = {word}

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
    return [pw for pw in variants if len(pw) >= min_len and (max_len is None or len(pw) <= max_len)]

def generate_name_combinations(name_input, config):
    parts = str(name_input).strip().split()
    combos = []

    if len(parts) == 2:
        first, last = parts
        combos = [
            first + last,
            first + '_' + last,
            first + '.' + last,
            first + '-' + last,
            last + first
        ]
    else:
        combos = [str(name_input).strip()]

    if config.get('use_years', False):
        long_true = config.get('use_long_years', False)
        short_true = config.get('use_short_years', False)
        all_years = config.get('years', [])

        filtered_years = []
        for y in all_years:
            y = str(y)
            if (long_true and len(y) == 4) or (short_true and len(y) == 2):
                filtered_years.append(y)
        for base in combos[:]:
            if not any(y in base for y in filtered_years):
                combos.extend([base + y for y in filtered_years])

    if config.get('use_keyboard_walks', False):
        combos += [str(item) for item in config.get('keyboard_walks', [])]

    return combos

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
    if config.get('use_leetspeak', True):
        for word in all_mutants:
            leet_variants.update(
                leetspeak_realistic(
                    word,
                    config['real_world_leet'],
                    max_subs=2
                )
            )

    full_set = all_mutants.union(random_caps_variants)
    if config.get('use_leetspeak', True):
        full_set = full_set.union(leet_variants)

    return filter_by_length(
        full_set,
        min_len=config['min_password_length'],
        max_len=config['max_password_length']
    )

def get_output_filename(base_word, part_num, use_compression):
    fn = f"{str(base_word).replace(' ', '_')}_mutations_part{part_num}.txt"
    if use_compression:
        fn += ".gz"
    return fn

def main():
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser()
    parser.add_argument('--no-symbols', action='store_true', help='Disable symbol insertion.')
    parser.add_argument('--no-leetspeak', action='store_true', help='Disable leetspeak substitutions.')
    parser.add_argument('--no-keyboard-walk', action='store_true', help='Disable keyboard walk additions.')
    parser.add_argument('--no-compress', action='store_true', help='Disable gzip compression of output.')
    parser.add_argument('--names', choices=['none', 'us', 'uk'], default='none', help="Use a name list: 'us', 'uk', or 'none' (default manual input).")
    args = parser.parse_args()

    config = load_config('config.yaml')

    if not config.get('use_symbols', True):
        config['symbols'] = []

    if args.no_symbols:
        config['symbols'] = []
    if args.no_leetspeak:
        config['use_leetspeak'] = False
    if args.no_keyboard_walk:
        config['use_keyboard_walks'] = False
    if args.no_compress:
        config['use_compression'] = False

    use_compression = config.get('use_compression', False)
    max_lines_per_file = config.get('max_lines_per_file', 0)

    print("\nPassword Mutation Generator")

    name_combos = []
    if args.names == 'us':
        first_names, last_names = load_names('names_us.yaml')
        if not first_names or not last_names:
            print("[!] No valid US names found. Exiting.")
            return
        for first in first_names:
            for last in last_names:
                combined = f"{first.strip()} {last.strip()}"
                name_combos.extend(generate_name_combinations(combined, config))
        base_word = "names_us"
        print(f"\nLoaded {len(first_names)} US first names and {len(last_names)} last names.")
        print(f"Generated {len(name_combos)} base combinations.")
        
    elif args.names == 'uk':
        first_names, last_names = load_names('names_uk.yaml')
        if not first_names or not last_names:
            print("[!] No valid UK names found. Exiting.")
            return
        for first in first_names:
            for last in last_names:
                combined = f"{first.strip()} {last.strip()}"
                name_combos.extend(generate_name_combinations(combined, config))
        base_word = "names_uk"
        print(f"\nLoaded {len(first_names)} UK first names and {len(last_names)} last names.")
        
    else:
        base_word = input("Enter a single word or 'First Last': ").strip()
        if not base_word:
            print("No input received. Exiting.")
            return
        name_combos = generate_name_combinations(base_word, config)

    print(f"\nGenerating mutations for: '{base_word}'")
    print(f"Symbols: {' '.join(config['symbols']) if config['symbols'] else 'NONE'}")
    print(f"Max insertions: {config['max_symbols']}")
    print(f"Random caps per variant: {config['random_caps_per_variant']}")

    print(f"Leetspeak substitutions: {'ENABLED' if config.get('use_leetspeak', True) else 'DISABLED'}")
    print(f"Keyboard walks: {'ENABLED' if config.get('use_keyboard_walks', False) else 'DISABLED'}")
    print(f"Years added: {'ENABLED' if config.get('use_years', False) else 'DISABLED'}")
    print(f"Long years: {'ENABLED' if config.get('use_long_years', False) else 'DISABLED'}")
    print(f"Short years: {'ENABLED' if config.get('use_short_years', False) else 'DISABLED'}")
    
    if max_lines_per_file:
        print(f"Splitting output files every {max_lines_per_file:,} lines.")

    cpu_cores = multiprocessing.cpu_count()
    part_num = 1
    lines_in_part = 0
    total_written = 0
    
    output_file = get_output_filename(base_word, part_num, use_compression)
    file_open = gzip.open if use_compression else open
    file_args = {'mode': 'wt', 'encoding': 'utf-8'}

    start_time = time.time()
    
    f = file_open(output_file, **file_args)
    try:
        with multiprocessing.Pool(processes=cpu_cores) as pool:
            for result in pool.starmap(generate_password_variants, [(word, config) for word in name_combos]):
                for variant in result:
                    f.write(variant + '\n')
                    total_written += 1
                    lines_in_part += 1
                    if max_lines_per_file and lines_in_part >= max_lines_per_file:
                        f.close()
                        part_num += 1
                        lines_in_part = 0
                        output_file = get_output_filename(base_word, part_num, use_compression)
                        f = file_open(output_file, **file_args)
    finally:
        f.close()

    elapsed = time.time() - start_time
    print(f"\nGenerated {total_written:,} password variants in {part_num} file(s).")
    print(f"Time to generate: {elapsed:.2f} seconds")
    print(f"Last saved file: {output_file}")

if __name__ == "__main__":
    main()
