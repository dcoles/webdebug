#!/usr/bin/env python2
# Web-based Python Debugger
#
# Author: David Coles <dcoles@google.com>
from __future__ import print_function

import argparse
import os
import sys

from flask import Flask, render_template, request
import lldb

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def index_view():
    thread = process.GetThreadByIndexID(int(request.args["thread"])) if "thread" in request.args else process.selected_thread
    frame = thread.frame[int(request.args["frame"])] if "frame" in request.args else thread.frame[0]

    if request.method == "POST":
        action = request.form["action"]
        if action == "step_over":
            thread.StepOver()
        elif action == "step_into":
            thread.StepInto()
        elif action == "step_out":
            thread.StepOut()
        elif action == "continue":
            process.Continue()
        elif action == "kill":
            process.Kill()

    source = None
    try:
        source = open(str(frame.line_entry.file)).read()
    except IOError:
        pass

    context = {
        "debugger": debugger,
        "target": target,
        "process": process,
        "frame": frame,
        "source": source,
    }
    return render_template('index.html', **context)


@app.route('/breakpoints')
def breakpoints_view():
    return render_template('breakpoints.html', breakpoints=target.breakpoint_iter())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('executable')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    debugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)

    target = debugger.CreateTargetWithFileAndArch(args.executable, lldb.LLDB_ARCH_DEFAULT)
    if not target:
        print("ERROR: Failed to create target", file=sys.stderr)
        sys.exit(1)

    main_bp = target.BreakpointCreateByName("main", target.GetExecutable().GetFilename())
    print(main_bp)

    process = target.LaunchSimple(args.args, list(os.environ), os.getcwd())
    if not process:
        print("ERROR: Failed to launch process", file=sys.stderr)
        sys.exit(1)

    print(process)

    # XXX: Don't serve public with debug enabled! Flask exposes a remote console.
    app.run(debug=True)
