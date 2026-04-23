# Spellcast Solver

Ein leistungsstarker 5x5 Wortlöser, der in Python mit einer modernen Benutzeroberfläche (`customtkinter`) entwickelt wurde und **speziell für die Discord-Aktivität "Spellcast" konzipiert ist**. Bitte beachten Sie, dass dies *kein* universeller Boggle-Solver ist. Dieser Solver hilft Ihnen, die Wörter mit den meisten Punkten auf einem Spellcast-Brett zu finden, und berücksichtigt dabei spezielle Felder wie Diamanten, Doppelwort (DW), Doppelbuchstabe (DL), Dreifachbuchstabe (TL) und sogar Buchstaben-Joker (Swaps)!

## Funktionen
- **Interaktives 5x5-Raster**: Klicken und tippen Sie Ihre Buchstaben direkt in das Raster ein.
- **Spezialfeld-Markierungen**: Markieren Sie ganz einfach Diamanten und Multiplikatoren, um die absolute maximale Punktzahl zu berechnen.
- **Joker-Unterstützung (Swaps)**: Konfigurieren Sie die Anzahl der erlaubten Jokertausche, und lassen Sie den Solver die komplexesten Wörter finden.
- **Multithreading**: Nutzt Ihre gesamte CPU-Leistung durch parallele Berechnungen, um den Suchbaum rasend schnell abzuschließen.
- **Visuelle Pfadhervorhebung**: Fahren Sie mit der Maus über ein Ergebniswort, um den Weg auf dem Raster nachzuzeichnen, oder klicken Sie darauf, um ihn dauerhaft zu fixieren. Wenn Sie einen Buchstaben tauschen müssen, wird er mit einem Sternchen `*` markiert.
- **Internationalisierung**: UI unterstützt dynamisch Englisch, Französisch, Deutsch und Spanisch.

## Installation
1. Stellen Sie sicher, dass **Python 3.10+** installiert ist.
2. Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   ```
3. Installieren Sie die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

## Bedienung
Starten Sie die Benutzeroberfläche:
```bash
python solver/main.py
```
Füllen Sie die Buchstaben aus, wählen Sie Ihre Multiplikatoren und geben Sie an, wie viele Threads Sie verwenden möchten. Klicken Sie auf **"Wörter finden!"** 

## Lizenz
Dieses Projekt ist unter der **MIT-Lizenz** lizenziert. Es steht Ihnen frei, diese Software zu kopieren, zu verändern und zu verbreiten, vorausgesetzt, Sie fügen den ursprünglichen Urheberrechtshinweis hinzu und geben den Ersteller an. Weitere Details finden Sie in der `LICENSE`-Datei.
