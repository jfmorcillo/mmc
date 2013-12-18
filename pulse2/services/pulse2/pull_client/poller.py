# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Pulse Pull Client.
#
# Pulse Pull client is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse Pull Client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
#import os
import logging
#import pickle
import importlib
from threading import Thread, Event
from Queue import Queue

from command import Command
from workers import ResultWorker, StepWorker
from config import PullClientConfig


logger = logging.getLogger(__name__)


class QueueFinished(object):
    pass


class Poller(Thread):
    commands = []
    workers = []

    def __init__(self, stop, **kwargs):
        Thread.__init__(self, **kwargs)
        # Get config
        self.config = PullClientConfig.instance()
        # Instantiate DLP client
        mod_name, class_name = self.config.Dlp.client.rsplit('.', 1)
        module = importlib.import_module(mod_name)
        self.dlp_client = getattr(module, class_name)()
        # stop event for stopping the DLP poller
        self.stop = stop
        self.stop_workers = Event()
        # queues for workers
        # self.parallel_queue: wol, upload, delete steps
        # self.simple_queue: execution, inventory step
        # self.result_queue: all steps results
        self.parallel_queue = Queue()
        self.simple_queue = Queue()
        self.result_queue = Queue()
        for n in range(0, self.config.Poller.result_workers):
            self.workers.append(ResultWorker(self.stop_workers, self.result_queue, self.dlp_client))
        # only one worker for the execution step
        self.workers.append(StepWorker(self.stop_workers, self.simple_queue, self.result_queue))
        for n in range(0, self.config.Poller.parallel_workers):
            self.workers.append(StepWorker(self.stop_workers, self.parallel_queue, self.result_queue))
        logger.info("Starting workers")
        for worker in self.workers:
            worker.start()

    def run(self):
        while not self.stop.is_set():
            for cmd_dict in self.dlp_client.get_commands():
                if self.is_new_command(cmd_dict):
                    command = Command(cmd_dict, (self.parallel_queue, self.simple_queue), self.dlp_client)
                    self.commands.append(command)

            logger.info("Status:\n%s" % "\n".join(map(str, self.commands)))
            self.stop.wait(self.config.Poller.poll_interval)

        logger.info("Stopping workers")
        self.stop_workers.set()
        for worker in self.workers:
            worker.join()
        logger.info("Done")

    #def save_state(self):
        #with open(self.state_file, 'w+') as f:
            #pickle.dump(self.commands, f)

    #def restore_state(self):
        #if os.path.exists(self.state_file):
            #with open(self.state_file, 'r') as f:
                #self.commands = pickle.load(f)
            #os.unlink(self.state_file)

    def is_new_command(self, cmd_dict):
        for command in list(self.commands):
            # command has been rescheduled
            if command.id == cmd_dict['id'] and command.is_failed:
                # removing old failed command
                logger.info("Removing old command %s" % command.id)
                self.commands.remove(command)
                return True
            if command.id == cmd_dict['id'] and command.is_running:
                logger.info("Command %s is already running, ignoring..." % cmd_dict['id'])
                return False
        return True


if __name__ == "__main__":
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    h = logging.StreamHandler()
    h.setFormatter(formatter)
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG)

    stop = Event()
    p = Poller(stop)
    p.start()
    try:
        while p.is_alive():
            p.join(500)
    except KeyboardInterrupt:
        print "Exiting."
        stop.set()
        p.join()
        print "Bye bye!"