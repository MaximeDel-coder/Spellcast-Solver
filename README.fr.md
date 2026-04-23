# Solveur Spellcast

Un puissant solveur développé en Python avec une interface graphique moderne (`customtkinter`), **conçu spécifiquement pour l'activité Discord "Spellcast"**. Veuillez noter qu'il ne s'agit *pas* d'un solveur Boggle généraliste. Ce programme vous aide à trouver les mots rapportant le plus de points sur un plateau Spellcast en tenant compte des cases spéciales comme les Diamants, Mots Doubles, Lettres Doubles/Triples, ainsi que l'utilisation de jokers (swaps) !

## Aperçu de l'interface

<p align="center">
  <img src="images/default_interface.png" width="45%" alt="Interface par défaut" />
  <img src="images/solver_in_use.png" width="45%" alt="Solveur en cours d'utilisation" />
</p>
<p align="center">
  <img src="images/light_mode.png" width="45%" alt="Mode Clair" />
  <img src="images/language_menu.png" width="45%" alt="Menu des langues" />
</p>

## Fonctionnalités
- **Grille interactive 5x5** : Tapez directement vos lettres dans une interface ergonomique.
- **Marquage des cases spéciales** : Placez facilement vos diamants et vos multiplicateurs pour un calcul méticuleux.
- **Support des Jokers (Swaps)** : Configurez le nombre de lettres que vous avez le droit d'échanger pour débloquer des mots précieux.
- **Recherche Multithread** : Utilise tous les coeurs de votre processeur pour calculer rapidement tous les tracés possibles dans le dictionnaire.
- **Mise en évidence du tracé** : Survolez un mot dans la liste pour voir son tracé, ou cliquez dessus pour verrouiller son affichage sur la grille de façon permanente. Les jokers sont marqués d'une étoile `*` !
- **Internationalisation** : Interface multilingue (Anglais, Français, Allemand, Espagnol).
- **Mode Sombre/Clair** : Thème visuel personnalisable par une glissière élégante.

## Structure du projet
- `solver/main.py` : L'application graphique principale. Point d'entrée du programme.
- `solver/solver_core.py` : Le moteur algorithmique de calcul de score (DFS).
- `solver/dictionary.csv` : Le dictionnaire des mots valides.
- `build_dictionary.py` : Script utilitaire utilisant `nltk` pour reconstituer un dictionnaire depuis la base WordNet.
- `tests/test_solver.py` : Suite de tests unitaires garantissant la stabilité de la logique mathématique.

## Installation

1. Assurez-vous d'avoir installé **Python 3.10+**.
2. Clonez ou téléchargez ce dépôt.
3. Il est fortement conseillé d'utiliser un environnement virtuel :
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```
4. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```

## Comment utiliser le solveur

1. Lancer l'interface :
   ```bash
   python solver/main.py
   ```
2. **Étape Lettres** : Remplissez la grille 5x5 en tapant vos caractères. Le curseur avance tout seul.
3. **Options** : Utilisez la barre centrale pour sélectionner "Diamants", "Mot Double", etc. et cliquez sur les cases pour les assigner.
4. **Jokers et Threads** : Précisez le nombre de jokers (swaps) dont vous disposez et choisissez le nombre d'unités de calcul de votre processeur à allouer (0 pour l'utiliser intégralement).
5. **Chercher les mots !** : Lancez le calcul. L'application trouvera tous les mots jouables et les triera selon les points prioritaires, ou bien selon la quantité de diamants qu'ils rapportent.
6. **Mise en évidence** : Au survol d'un résultat, le dessin à réaliser physiquement sur votre écran pour relier les lettres va s'afficher sur la grille avec des numéros.

## Licence

Ce projet est publié sous le couvert de la **Licence MIT**. Vous êtes libre de copier, modifier, utiliser et distribuer ce code source (commercialement ou non), à la condition stricte d'inclure la mention originale du droit d'auteur (attribution au créateur) présente dans le fichier `LICENSE`.
