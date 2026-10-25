# Dining Philosophers (4) solved with semaphores.
# Running this file creates dining_philosophers_semaphore.html from the real execution events.

import threading
import time
import random
import json

NUM = 4               # philosophers (and forks)
ROUNDS = 3            # how many times each philosopher eats
MAX_DELAY = 0.6       # upper limit for random sleeps (seconds)

# Philosopher i uses fork i (left) and fork (i+1) % NUM (right).
fork_owner = [-1] * NUM    # -1 = fork is free, otherwise the philosopher holding it

log_lock = threading.Lock()
events = []
start_time = time.time()


def log(who, state, note=""):
    """Save one state change together with who currently holds each fork."""
    with log_lock:
        events.append({
            "time": round(time.time() - start_time, 3),
            "who": who,
            "state": state,
            "note": note,
            "forks": list(fork_owner),
        })


def pause():
    time.sleep(random.uniform(0.1, MAX_DELAY))


forks = [threading.Semaphore(1) for _ in range(NUM)]   # one semaphore per fork
# Deadlock prevention: at most NUM-1 philosophers may try to pick up forks at once.
# If all 4 grabbed their left fork together, nobody could get a right fork (deadlock).
# With only 3 allowed, at least one philosopher can always get both forks.
room = threading.Semaphore(NUM - 1)


def philosopher(i):
    left = i
    right = (i + 1) % NUM
    for _ in range(ROUNDS):
        log(i, "thinking")
        pause()

        log(i, "hungry", "wants to eat")
        room.acquire()                      # enter the "room" (max 3 at a time)

        log(i, "acquiring", "picking up forks")
        forks[left].acquire()
        fork_owner[left] = i
        log(i, "acquiring", "has left fork " + str(left))
        forks[right].acquire()
        fork_owner[right] = i

        # ---- critical section (eating, uses both forks) ----
        log(i, "eating", "has forks " + str(left) + " and " + str(right))
        pause()
        # ----------------------------------------------------

        log(i, "releasing", "putting forks down")
        fork_owner[left] = -1
        forks[left].release()
        fork_owner[right] = -1
        forks[right].release()
        room.release()


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Dining Philosophers (Semaphore)</title>
<style>
  body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
  #main { display: flex; gap: 20px; flex-wrap: wrap; }
  #forks { background: white; padding: 10px; border: 1px solid #aaa; width: 220px; }
  #log { height: 200px; overflow-y: scroll; background: white; padding: 8px;
         border: 1px solid #aaa; font-size: 13px; margin-top: 10px; }
  button { padding: 6px 14px; margin-right: 5px; }
</style>
</head>
<body>
<h2>Dining Philosophers (4) - Semaphore Version</h2>
<div>
  <button onclick="start()">Start</button>
  <button onclick="pauseSim()">Pause</button>
  <button onclick="resetSim()">Reset</button>
  Speed (ms/event): <input id="speed" type="number" value="500" style="width:60px">
</div>
<p>
  States: <b style="color:#777">Thinking</b> |
  <b style="color:#e0a000">Hungry</b> |
  <b style="color:#8040c0">Acquiring forks</b> |
  <b style="color:#2a8a2a">Eating</b> |
  <b style="color:#3070c0">Releasing forks</b>
  &nbsp;&nbsp; Fork: green = free, red = held
</p>
<div id="main">
  <div id="picture"></div>
  <div>
    <div id="forks"></div>
    <div id="log"></div>
  </div>
</div>

<script>
var events = __EVENTS__;
var N = 4;
var index = 0;
var timer = null;
var states = [];
var owner = [];
var colours = { thinking: "#888", hungry: "#e0a000", acquiring: "#8040c0",
                eating: "#2a8a2a", releasing: "#3070c0" };

function resetData() {
  states = [];
  owner = [];
  for (var i = 0; i < N; i++) { states.push("thinking"); owner.push(-1); }
}

function pos(angle, r) {
  var a = angle * Math.PI / 180 - Math.PI / 2;
  return [200 + r * Math.cos(a), 200 + r * Math.sin(a)];
}

function draw() {
  var s = "<svg width='400' height='400' style='background:white;border:1px solid #aaa'>";
  s += "<circle cx='200' cy='200' r='85' fill='#e8d8b8' stroke='#999'/>";
  for (var i = 0; i < N; i++) {
    var q = pos(i * 90, 150);
    s += "<circle cx='" + q[0] + "' cy='" + q[1] + "' r='38' fill='" + colours[states[i]] + "'/>";
    s += "<text x='" + q[0] + "' y='" + (q[1] - 3) + "' fill='white' font-size='13' text-anchor='middle'>P" + i + "</text>";
    s += "<text x='" + q[0] + "' y='" + (q[1] + 12) + "' fill='white' font-size='10' text-anchor='middle'>" + states[i] + "</text>";
  }
  var info = "<b>Fork ownership</b><br>";
  for (var k = 0; k < N; k++) {
    var base = pos(k * 90 - 45, 95);
    var p = base;
    var colour = "#2a8a2a";
    if (owner[k] >= 0) {
      var ph = pos(owner[k] * 90, 140);
      p = [base[0] + 0.6 * (ph[0] - base[0]), base[1] + 0.6 * (ph[1] - base[1])];
      colour = "#c03030";
      info += "Fork " + k + ": held by P" + owner[k] + "<br>";
    } else {
      info += "Fork " + k + ": free<br>";
    }
    s += "<circle cx='" + p[0] + "' cy='" + p[1] + "' r='11' fill='" + colour + "'/>";
    s += "<text x='" + p[0] + "' y='" + (p[1] + 4) + "' font-size='11' fill='white' text-anchor='middle'>F" + k + "</text>";
  }
  s += "</svg>";
  document.getElementById("picture").innerHTML = s;
  document.getElementById("forks").innerHTML = info;
}

function step() {
  if (index >= events.length) { pauseSim(); return; }
  var e = events[index];
  states[e.who] = e.state;
  owner = e.forks.slice();
  draw();
  var line = "[" + e.time + "s] P" + e.who + " -> " + e.state + " " + e.note;
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
  resetData();
  document.getElementById("log").innerHTML = "";
  draw();
}
resetData();
draw();
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
    for i in range(NUM):
        threads.append(threading.Thread(target=philosopher, args=(i,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    make_html("dining_philosophers_semaphore.html")
    print("Finished. Every philosopher ate", ROUNDS, "times, no deadlock.")
    print("Events recorded:", len(events))
    print("Open dining_philosophers_semaphore.html in your browser.")


if __name__ == "__main__":
    main()
