from collections import Counter, defaultdict
import csv
import random

def find_frequencies(words):
    counter = Counter()
    for word in words:
        for c in word:
            counter[c] += 1
    return counter

def find_words_matching(words, known, included_letters, excluded_letters):
    matching_words =[]
    for word in words:
        if all(l not in word for l in excluded_letters) and all(word.find(l) in indices for l, indices in included_letters.items()) and all(word[i] == k for k, i in known.items()):
                matching_words.append(word)
    return matching_words

def find_best_guess_frequency(words, known, include, exclude, previous_guesses):
    filtered_words = find_words_matching(words, known, include, exclude)
    frequencies = find_frequencies(filtered_words)
    best_guess = None
    best_guess_score = 0
    for word in filtered_words:
        if word in previous_guesses:
            continue
        score = sum(frequencies[c] for c in set(word))
        if score > best_guess_score:
            best_guess = word
            best_guess_score = score
    return best_guess

def find_best_guess_random(words, known, include, exclude, previous_guesses):
    filtered_words = [ f for f in find_words_matching(words, known, include, exclude) if f not in previous_guesses]
    return random.choice([f for f in filtered_words if f not in previous_guesses]) if len(filtered_words) > 0 else None

def find_best_guess_popularity(words, known, include, exclude, previous_guesses, frequencies):
    filtered_words = [f for f in find_words_matching(words, known, include, exclude) if f not in previous_guesses]
    best_guess = None
    best_guess_score = 0
    for word in filtered_words:
        score = frequencies.get(word, 1)
        if score > best_guess_score:
            best_guess = word
            best_guess_score = score
    return best_guess


def calculate_feedback(target_word, guessed_word):
    result = ""
    for i, w in enumerate(guessed_word):
        if w == target_word[i]:
            result += 'g'
        else:
            if w in target_word:
                result += 'y'
            else:
                result += 'b'
    return result

def update_contraints(result, guess, known, includes, excludes):
    for i, r in enumerate(result):
        c = guess[i]
        if r == 'g':
            known[c] = i
        elif r == 'y':
            includes[c] = [j for j in includes[c] if j != i]
        elif r == 'b':
            excludes.add(c)
        else:
            raise ValueError(f'unexpected char in result string: {r}')

def run_manual(words, frequencies):
    known = {}
    includes = defaultdict(lambda: [0,1,2,3,4])
    excludes = set()
    guesses = []

    while True:
        next_guess = find_best_guess_random(words, known, includes, excludes, guesses)
        guesses.append(next_guess)
        print(f"Next guess: {next_guess}")
        print("Enter result eg. gggyb for green green green yellow black")
        result = input()
        if len(result) != 5 or not all(r in 'gyb' for r in result ):
            print('incorrect input try again')
            continue

        if result == 'ggggg':
            print('Easy pickings')
            return

        update_contraints(result, next_guess, known, includes, excludes)

def run_game(words, target, frequencies):
    known = {}
    includes = defaultdict(lambda: [0,1,2,3,4])
    excludes = set()
    result = 'bbbbb'
    guesses = []

    while result != 'ggggg':
        next_guess = find_best_guess_popularity(words, known, includes, excludes, guesses, frequencies)
        guesses.append(next_guess)
        if not next_guess:
            print(f"failed to get to target: {target}. Guesses: {guesses}")
            return guesses

        result = calculate_feedback(target, next_guess)
        update_contraints(result, next_guess, known, includes, excludes)
    return guesses

def main():
    words = set()
    with open('./five-letter-words.txt') as f:
        words.update(line.strip() for line in f)

    with open('./frequent-words.csv') as f:
        reader = csv.DictReader(f, delimiter='\t')
        word_frequencies = Counter()
        for row in reader:
            word = row['word']
            frequency = row['wordFreq']
            if len(word) == 5 and word in words:
                word_frequencies[word] = int(frequency)

    print(run_game(words, 'whack', word_frequencies))
    exit()
    guess_counts = Counter()
    for target in word_frequencies.most_common():
        path = run_game(words, target[0], word_frequencies)
        steps = len(path)
        guess_counts[steps] += 1
        if steps > 6:
            print(f"target: {target[0]}, guesses: {path}")

    print(guess_counts.most_common())


if __name__ == "__main__":
    main()
