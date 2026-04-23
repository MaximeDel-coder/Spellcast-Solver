import nltk
from nltk.corpus import wordnet as wn
import csv
import os

def main():
    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate_csv = os.path.join(script_dir, "wordnet_raw_dictionary.csv")
    final_csv = os.path.join(script_dir, "solver", "dictionary.csv")

    print("[1/3] Downloading WordNet database (if necessary)...")
    nltk.download('wordnet')

    words = set()

    print("[2/3] Extracting English words from WordNet...")
    for synset in wn.all_synsets():
        for lemma in synset.lemmas():
            word = lemma.name().replace('_', ' ')
            # Filter to keep only alphabetical words with at least 5 letters
            if word.isalpha() and len(word) >= 5:
                words.add(word.lower())

    words = sorted(words)

    # Save the intermediate raw lowercase file at the root folder
    with open(intermediate_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['word'])
        for word in words:
            writer.writerow([word])
    print(f"      -> {len(words)} raw lowercase words saved in {intermediate_csv}")

    print("[3/3] Final formatting (uppercase conversion) for the solver...")
    words_upper = [w.upper() for w in words]

    # Ensure the solver dictionary directory exists
    os.makedirs(os.path.dirname(final_csv), exist_ok=True)
    with open(final_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['word'])
        for word in words_upper:
            writer.writerow([word])
    print(f"      -> Final solver dictionary successfully generated at {final_csv}")
    print("\n[Complete] Dictionary updated successfully!")

if __name__ == "__main__":
    main()
