import threading
import random
import time

NUM_TELLERS = 3
NUM_CUSTOMERS = 50

# --- Synchronization primitives ---

door_sem = threading.Semaphore(2)      # Only 2 customers in the bank at a time
manager_sem = threading.Semaphore(1)   # Only 1 teller can talk to manager
safe_sem = threading.Semaphore(2)      # Only 2 tellers can be in safe

queue_sem = threading.Semaphore(0)     # Counts customers waiting in line
queue_lock = threading.Lock()
customer_queue = []

bank_open_event = threading.Event()
tellers_ready_lock = threading.Lock()
tellers_ready_count = 0

closing = False
closing_lock = threading.Lock()


class CustomerInfo:
    def __init__(self, cid, transaction):
        self.cid = cid
        self.transaction = transaction  # "deposit" or "withdrawal"
        self.teller_id = None

        # Per-customer semaphores for coordination
        self.selected_sem = threading.Semaphore(0)
        self.ask_txn_sem = threading.Semaphore(0)
        self.txn_given_sem = threading.Semaphore(0)
        self.done_sem = threading.Semaphore(0)


def teller_thread(tid: int):
    global tellers_ready_count, closing

    first_time = True

    while True:
        print(f"Teller {tid} []: ready to serve")
        print(f"Teller {tid} []: waiting for a customer")

        # First time this teller becomes ready, contribute to "bank open"
        if first_time:
            with tellers_ready_lock:
                tellers_ready_count += 1
                if tellers_ready_count == NUM_TELLERS:
                    bank_open_event.set()
            first_time = False

        queue_sem.acquire()

        with closing_lock:
            if closing:
                print(f"Teller {tid} []: leaving for the day")
                return

        with queue_lock:
            if not customer_queue:
                continue
            cust = customer_queue.pop(0)

        cid = cust.cid
        cust.teller_id = tid
        cust.selected_sem.release()

        print(f"Teller {tid} [Customer {cid}]: serving a customer")
        print(f"Teller {tid} [Customer {cid}]: asks for transaction")
        cust.ask_txn_sem.release()
        cust.txn_given_sem.acquire()

        if cust.transaction == "withdrawal":
            # Withdrawal path: manager + safe
            print(f"Teller {tid} [Customer {cid}]: handling withdrawal transaction")
            print(f"Teller {tid} [Customer {cid}]: going to the manager")
            manager_sem.acquire()
            print(f"Teller {tid} [Customer {cid}]: getting manager's permission")
            time.sleep(random.uniform(0.005, 0.030))
            print(f"Teller {tid} [Customer {cid}]: got manager's permission")
            manager_sem.release()

            print(f"Teller {tid} [Customer {cid}]: going to safe")
            safe_sem.acquire()
            print(f"Teller {tid} [Customer {cid}]: enter safe")
            time.sleep(random.uniform(0.010, 0.050))
            print(f"Teller {tid} [Customer {cid}]: leaving safe")
            safe_sem.release()

            print(f"Teller {tid} [Customer {cid}]: finishes withdrawal transaction.")
        else:
            # Deposit path: safe only
            print(f"Teller {tid} [Customer {cid}]: handling deposit transaction")
            print(f"Teller {tid} [Customer {cid}]: going to safe")
            safe_sem.acquire()
            print(f"Teller {tid} [Customer {cid}]: enter safe")
            time.sleep(random.uniform(0.010, 0.050))
            print(f"Teller {tid} [Customer {cid}]: leaving safe")
            safe_sem.release()
            print(f"Teller {tid} [Customer {cid}]: finishes deposit transaction.")

        print(f"Teller {tid} [Customer {cid}]: wait for customer to leave.")
        cust.done_sem.release()


def customer_thread(cust: CustomerInfo):
    cid = cust.cid
    time.sleep(random.uniform(0.0, 0.100))

    bank_open_event.wait()

    print(f"Customer {cid} []: going to bank.")
    door_sem.acquire()
    print(f"Customer {cid} []: entering bank.")
    print(f"Customer {cid} []: getting in line.")

    with queue_lock:
        customer_queue.append(cust)
    queue_sem.release()

    cust.selected_sem.acquire()
    tid = cust.teller_id

    print(f"Customer {cid} []: selecting a teller.")
    print(f"Customer {cid} [Teller {tid}]: selects teller")
    print(f"Customer {cid} [Teller {tid}] introduces itself")

    cust.ask_txn_sem.acquire()
    if cust.transaction == "deposit":
        print(f"Customer {cid} [Teller {tid}]: asks for deposit transaction")
    else:
        print(f"Customer {cid} [Teller {tid}]: asks for withdrawal transaction")
    cust.txn_given_sem.release()

    cust.done_sem.acquire()
    print(f"Customer {cid} [Teller {tid}]: leaves teller")
    print(f"Customer {cid} []: goes to door")
    print(f"Customer {cid} []: leaves the bank")

    door_sem.release()


def main():
    global closing

    random.seed()

    tellers = []
    for tid in range(NUM_TELLERS):
        t = threading.Thread(target=teller_thread, args=(tid,))
        t.start()
        tellers.append(t)

    customers = []
    for cid in range(NUM_CUSTOMERS):
        transaction = random.choice(["deposit", "withdrawal"])
        print(f"Customer {cid} []: wants to perform a {transaction} transaction")
        cust = CustomerInfo(cid, transaction)
        customers.append(cust)

    threads = []
    for cust in customers:
        t = threading.Thread(target=customer_thread, args=(cust,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    with closing_lock:
        closing = True

    # Wake up each teller so they can see closing == True and exit
    for _ in range(NUM_TELLERS):
        queue_sem.release()

    for t in tellers:
        t.join()

    print("The bank closes for the day.")


if __name__ == "__main__":
    main()
