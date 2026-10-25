# OS Synchronization Assignment

Name: [YOUR NAME]
USN: [YOUR USN]

## What is in this repo
1. readers_writers/semaphore - Readers-Writers using semaphores
2. readers_writers/monitor - Readers-Writers using a monitor (lock + condition variables)
3. dining_philosophers/semaphore - 4 philosophers using semaphores
4. dining_philosophers/monitor - 4 philosophers using a monitor

## Language and requirements
Python 3 (no extra libraries, only the standard library).

## How to run (no build step needed)
    cd readers_writers/semaphore
    python rw_semaphore.py

Each program runs its threads, records the events, and writes an HTML file
into the folder you ran it from. Copy the HTML files into generated_html/.

## How to view the simulation
Double-click the generated .html file (or open it in Chrome/Firefox) and press Start.

## Screenshots
See the screenshots/ folder. [ADD YOUR OWN SCREENSHOTS]

## Known limitations
[WRITE YOUR OWN, e.g. readers-preference can starve writers in the semaphore version]

## AI tools used
[NAME THE TOOL] - prompts are in ai_prompts/prompts.md

## References
See references/references.md
