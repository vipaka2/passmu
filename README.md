# Passmu (Password Mutation Generator)

Passmu is a powerful password mutation tool for security and penetration testing.

---

## Features

- **Random Capitalization**: randomly mixed uppercase and lowercase letters
- **First and Last**: concatenated, underscore, dot, hyphen, and reversed
- **Capitalization**: lowercase, uppercase, capitalized, and title case
- **Symbol and Number**: before, after, and inside the word
- **Max Lines Per File**: control how many lines per file
- **Config**: YAML config file for easy customization
- **Leetspeak**: real-world leetspeak substitutions
- **On-the-fly compression**: save output to gzip

## CLI

``> Password Mutation Generator ``

``> Enter a single word or 'first last': dragon ``

``> Generated 1,639,943 password variants in 1 file(s).``

``> Time to generate: 2.02 seconds``

``> Last saved file: dragon_mutations_part1.txt``

## Config

```
max_lines_per_file: 10000000
random_caps_per_variant: 2
max_password_length: 24
min_password_length: 8
max_symbols: 2

use_short_years: true
use_long_years: false
use_years: true

use_keyboard_walks: false
use_compression: false
use_leetspeak: false

symbols: ['!', '@', '#', '$', '%', '&', '*', '?', '1', '2', '3', '.', '_', '-']
real_world_leet:
  a: ['@', '4']
  e: ['3']
  i: ['1', '!']
  o: ['0']
  s: ['$', '5']
  t: ['7']
  l: ['1']
  b: ['8'] 
  g: ['9']
  z: ['2']
keyboard_walks:
  - qwerty
  - asdfgh
  - zxcvbn
  - 123456
  - 654321
  - qazwsx
  - 1qaz2wsx
  - qweasd
  - poiuy
  - mnbvcx
years: 
  - "2025"
  - "2024"
  - "2023"
  - "02"
  - "01"
  - "00"
```
