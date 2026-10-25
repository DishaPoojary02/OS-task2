# Readers-Writers problem solved with semaphores.
# Running this file creates readers_writers_semaphore.html from the events
# that actually happened while the threads ran.

import threading
import time
import random
import json

NUM_READERS = 3
NUM_WRITERS = 2
ROUNDS = 3            # how many times each thread tries to access the data
MAX_DELAY = 0.6       # upper limit for random sleeps (seconds)

shared_data = 0       # the shared resource
read_count = 0        # number of readers currently inside

mutex = threading.Semaphore(1)       # protects read_count
resource = threading.Semaphore(1)    # held by a writer, or by the group of readers

log_lock = threading.Lock()          # so two threads don't append to the log at once
events = []
start_time = time.time()


def log(who, state, note=""):
    """Save one state change. This list is what the HTML is built from."""
    with log_lock:
        events.append({
            "time": round(time.time() - start_time, 3),
            "who": who,
            "state": state,
            "value": shared_data,
            "note": note,
        })


def pause():
    time.sleep(random.uniform(0.1, MAX_DELAY))


def reader(reader_id):
    global read_count
    name = "Reader " + str(reader_id)
    for _ in range(ROUNDS):
        log(name, "thinking")
        pause()

        log(name, "waiting", "wants to read")
        mutex.acquire()
        read_count += 1
        if read_count == 1:
            resource.acquire()       # first reader locks out the writers
        mutex.release()

        # ---- critical section (reading) ----
        log(name, "reading", "read value " + str(shared_data))
        pause()
        log(name, "done", "finished reading")
        # ------------------------------------

        mutex.acquire()
        read_count -= 1
        if read_count == 0:
            resource.release()       # last reader lets writers in
        mutex.release()


def writer(writer_id):
    global shared_data
    name = "Writer " + str(writer_id)
    for _ in range(ROUNDS):
        log(name, "thinking")
        pause()

        log(name, "waiting", "wants to write")
        resource.acquire()

        # ---- critical section (writing) ----
        shared_data += 1
        log(name, "writing", "wrote value " + str(shared_data))
        pause()
        log(name, "done", "finished writing")
        # ------------------------------------

        resource.release()


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Readers-Writers (Semaphore)</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
  #actors { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
  .box { width: 130px; padding: 12px; border-radius: 8px; text-align: center;
         color: white; background: #888; }
  .thinking { background: #888; }
  .waiting  { background: #e0a000; }
  .reading  { background: #2a8a2a; }
  .writing  { background: #c03030; }
  .done     { background: #3070c0; }
  #resource { padding: 12px; background: white; border: 2px solid #333;
              border-radius: 8px; margin-bottom: 10px; }
  #log { height: 220px; overflow-y: scroll; background: white; padding: 8px;
         border: 1px solid #aaa; font-size: 13px; }
  button { padding: 6px 14px; margin-right: 5px; }
</style>
</head>
<body>
<h2>Readers-Writers Problem - Semaphore Version</h2>
<div>
  <button onclick="start()">Start</button>
  <button onclick="pauseSim()">Pause</button>
  <button onclick="resetSim()">Reset</button>
  Speed (ms/event): <input id="speed" type="number" value="500" style="width:60px">
</div>
<div id="resource"></div>
<div id="actors"></div>
<h3>Event timeline</h3>
<div id="log"></div>

<script>
var events = __EVENTS__;
var index = 0;
var timer = null;
var states = {};

// build the list of threads from the events
events.forEach(function (e) { states[e.who] = "thinking"; });

function draw(value) {
  var readers = 0, writers = 0;
  for (var name in states) {
    if (states[name] == "reading") readers++;
    if (states[name] == "writing") writers++;
  }
  var status = "FREE";
  if (writers > 0) status = "LOCKED by a writer (exclusive)";
  else if (readers > 0) status = "OPEN to " + readers + " reader(s)";
  document.getElementById("resource").innerHTML =
    "<b>Shared resource</b> value = " + value + " | status: " + status;

  var html = "";
  for (var name in states) {
    html += "<div class='box " + states[name] + "'>" + name + "<br>" + states[name] + "</div>";
  }
  document.getElementById("actors").innerHTML = html;
}

function step() {
  if (index >= events.length) { pauseSim(); return; }
  var e = events[index];
  states[e.who] = e.state;
  draw(e.value);
  var line = "[" + e.time + "s] " + e.who + " -> " + e.state + " " + e.note;
  document.getElementById("log").innerHTML += line + "<br>";
  document.getElementById("log").scrollTop = 99999;
  index++;
}

function start() {
  if (timer) return;
  timer = setInterval(step, document.getElementById("speed").value);
}
function pauseSim() { clearInterval(timer); timer = null; }
function resetSim() {
  pauseSim();
  index = 0;
  for (var name in states) states[name] = "thinking";
  document.getElementById("log").innerHTML = "";
  draw(0);
}
draw(0);
</script>
</body>
</html>
"""


def make_html(filename):
    page = HTML_TEMPLATE.replace("__EVENTS__", json.dumps(events))
    with open(filename, "w") as f:
        f.write(page)


def main():
    threads = []
    for i in range(1, NUM_READERS + 1):
        threads.append(threading.Thread(target=reader, args=(i,)))
    for i in range(1, NUM_WRITERS + 1):
        threads.append(threading.Thread(target=writer, args=(i,)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    make_html("readers_writers_semaphore.html")
    print("Finished. Final value =", shared_data)
    print("Events recorded:", len(events))
   


if __name__ == "__main__":
    main()
