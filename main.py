name: Bug Bounty Alert Bot

on:
  schedule:
    - cron: '0 * * * *' # Har ghante chalega
  workflow_dispatch: # Button to run manually

jobs:
  run-monitor:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Run Script
        env:
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        run: python main.py

      - name: Save Memory (Commit)
        run: |
          git config --global user.name "Bot Action"
          git config --global user.email "bot@github.com"
          git add known_programs.json || true
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update list" && git push)
