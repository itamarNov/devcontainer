from itertools import cycle
import random
import logging
import sys

NumberOfWords = 24

def get_user_words(all_words):
    print(f'Please enter your {NumberOfWords} words...')
    words = list()
    idx = 0
    while len(words) < NumberOfWords:
        word = input(f'Enter word #{idx + 1:02}:')
        if word not in all_words:
            print(f'The word {word} is not allowed')
            continue
        if word in words:
            print(f'The word {word} is already in your list. words in list must be unique')
            continue
        words.append(word)
        idx = idx + 1
    return words

def get_words_as_set(filename):
  words = set()
  try:
    with open(filename, 'r') as f:
      for line in f:
        # Split the line into words using whitespace as delimiter
        words.update(line.split())
  except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
  return words

def compare_two_files(file1, file2):
    words_set1 = get_words_as_set(file1)
    words_set2 = get_words_as_set(file2)
    return words_set1 == words_set2

def check_special_words_and_indexes(new_list, special_words, special_indexes):
    for word, idx in zip(special_words, special_indexes):
        if new_list[idx - 1] != word:
            raise ValueError(f'{new_list[idx]} in index {idx} instead of {word}')
    return True

def read_word_list():
    with open('english.txt', 'r') as file:
        lines = file.readlines()
        words = [x.removesuffix('\n') for x in lines]
    return words

def print_words(file_name, words, words_per_line=1):
    with open(file_name, 'w') as file:
        for i in range(0, len(words), words_per_line):
            # Get a slice of the list with n_per_line words
            line_words = words[i:i + words_per_line]
            # Join the words with spaces and add a newline character
            line = ' '.join(line_words) + '\n'
            file.write(line)

def print_words2(file_name, word_list, max_line_length=90):
    max_line = -1
    with open(file_name, 'w') as f:
        current_line = ""
        for word in word_list:
            # Check if adding the word will exceed the line length
            if len(current_line) + len(word) + 1 > max_line_length:  # Add 1 for space
                if len(current_line) > max_line:
                    max_line = len(current_line)
                f.write(current_line + '\n')
                current_line = ""
            current_line += word + " "
        # Write the last line (if not empty)
        f.write(current_line.strip())
    logging.info(f'Max line length is {max_line}')

def create_base_indexes(digits: str):
    assert all([x.isdigit() for x in digits]), f'Input must be all digits'
    assert all([x != '0' for x in digits]), f'Input can not include the 0 digit'
    return [int(x) for x in digits]

def create_increment_indexes(increments: list):
    idx = 0
    indexes = []
    iter1 = iter(cycle(increments))
    iter2 = iter(cycle(increments))
    next(iter2)
    while len(indexes) < NumberOfWords:
        # idx = idx + next(iter1)
        idx = idx + 10 * next(iter1) + next(iter2)
        indexes.append(idx)
    if (max_idx := indexes[-1]) > 2048:
        raise ValueError(f'Special indexes max value {max_idx} is bigger than 2048')
    return indexes

def get_run_mode():
    try:
        run_mode = sys.argv[1]
    except IndexError:
        run_mode = 'default'
    return run_mode

def create_list(base_list, special_indexes, special_words):
    initial_list = base_list[:]
    new_list = ['' for _ in range(len(initial_list))]

    for idx, word in zip(special_indexes, special_words):
        new_list[idx - 1] = word
        initial_list.remove(word)

    for new_list_idx in range(len(new_list)):
        if new_list[new_list_idx] == '':
            initial_list_idx = random.randint(0, len(initial_list) - 1)
            new_list[new_list_idx] = initial_list.pop(initial_list_idx)
    return new_list


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    run_mode = get_run_mode()
    logging.info(f'running mode: {run_mode}')

    all_words = read_word_list()
    if run_mode != 'deFault':
        special_words = random.sample(all_words, NumberOfWords)
    else:
        special_words = get_user_words(all_words)
    logging.info(f'your specific words are:\n{special_words}')

    default_indexes_seed = '123456789'
    indexes_seed = input(f"Enter indexes seed (default: {default_indexes_seed}): ") or default_indexes_seed
    logging.info(f'your indexes seed is: {indexes_seed}')
    base_indexes = create_base_indexes(indexes_seed)

    special_indexes = create_increment_indexes(base_indexes)
    logging.info(f'your special indexes are:\n{special_indexes}')


    logging.info(f'creating the list of words...')
    new_list = create_list(all_words, special_indexes, special_words)
    logging.debug(f'{new_list}')
    logging.debug(f'{sorted(new_list)}')

    output_file1 = 'hebrew001.txt' 
    logging.info(f'printing list of words to file {output_file1}, each word in a line...')
    print_words(output_file1, new_list, 1)
    line_length = 97
    output_file2 = f'hebrew{line_length:03}.txt'
    logging.info(f'printing list of words to file {output_file2}, each line of {line_length} character long...')
    print_words2(output_file2, new_list, line_length) # print with LibraOffice, Char size 9.7

    try:
        assert set(new_list) == set(sorted(new_list))
        logging.info(f'Checked OK: two lists contains the same words')
    except AssertionError:
        logging.error(f'\n\n\nChecked FAILED!!!!: two lists do not contains the same words\n\n\n')

    try:
        assert check_special_words_and_indexes(new_list, special_words, special_indexes)
        logging.info(f'Checked OK: special words are in special indexes')
    except AssertionError:
        logging.error(f'\n\n\nChecked FAILED!!!!: special words are not in special indexes\n\n\n')

    try:
        assert compare_two_files(output_file1, output_file2)
        logging.info(f'Checked OK: two output files equal')
    except AssertionError:
        logging.error(f'\n\n\nChecked FAILED!!!!: two output files are not equal\n\n\n')
