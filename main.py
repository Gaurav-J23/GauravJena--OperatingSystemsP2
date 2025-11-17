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
customer_queue = []                    # FIFO queue of waiting customers

# Bank open coordination
bank_open_event = threading.Event()
tellers_ready_lock = threading.Lock()
tellers_ready_count = 0

# Closing flag (set when all customers are done)
closing = False
closing_lock = threading.Lock()


class CustomerInfo:
    def __init__(self, cid, transaction):
        self.cid = cid
        # "deposit" or "withdrawal"
        self.transaction = transaction

        # Teller assigned to this customer
        self.teller_id = None

        # Per-customer semaphores for coordination
        self.selected_sem = threading.Semaphore(0)   # teller has chosen this customer
        self.ask_txn_sem = threading.Semaphore(0)    # teller asks for transaction
        self.txn_given_sem = threading.Semaphore(0)  # customer has told transaction
        self.done_sem = threading.Semaphore(0)       # teller finished, customer can leave


def teller_thread(tid: int):
    global tellers_ready_count, closing

    first_time = True

    while True:
        # Teller announces ready state
        print(f"Teller {tid} []: ready to serve")
        print(f"Teller {tid} []: waiting for a customer")

        # First time this teller becomes ready, contribute to "bank open"
        if first_time:
            with tellers_ready_lock:
                tellers_ready_count += 1
                if tellers_ready_count == NUM_TELLERS:
                    # All tellers are ready -> bank opens
                    bank_open_event.set()
            first_time = False

        # Wait for a customer to be available or for closing
        queue_sem.acquire()

        with closing_lock:
            if closing:
                # No more customers; teller leaves for the day
                print(f"Teller {tid} []: leaving for the day")
                return

        # Get the next customer from the line
        with queue_lock:
            if not customer_queue:
                # Could happen if we were woken up during closing
                continue
            cust = customer_queue.pop(0)

        cid = cust.cid
        cust.teller_id = tid
        # Signal customer that teller is ready for them
        cust.selected_sem.release()

        # Start serving this customer
        print(f"Teller {tid} [Customer {cid}]: serving a customer")
        print(f"Teller {tid} [Customer {cid}]: asks for transaction")
        cust.ask_txn_sem.release()     # Ask customer for transaction
        cust.txn_given_sem.acquire()   # Wait for customer to state it

        if cust.transaction == "withdrawal":
            # Withdrawal path: manager + safe
            print(f"Teller {tid} [Customer {cid}]: handling withdrawal transaction")
            print(f"Teller {tid} [Customer {cid}]: going to the manager")
            manager_sem.acquire()
            print(f"Teller {tid} [Customer {cid}]: getting manager's permission")
            # Sleep 5–30 ms
            time.sleep(random.uniform(0.005, 0.030))
            print(f"Teller {tid} [Customer {cid}]: got manager's permission")
            manager_sem.release()

            print(f"Teller {tid} [Customer {cid}]: going to safe")
            safe_sem.acquire()
            print(f"Teller {tid} [Customer {cid}]: enter safe")
            # Sleep 10–50 ms
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
        # Let customer know we are done
        cust.done_sem.release()


def customer_thread(cust: CustomerInfo):
    cid = cust.cid
    # Wait 0–100 ms before going to bank
    time.sleep(random.uniform(0.0, 0.100))

    # Wait until bank is open (all tellers ready)
    bank_open_event.wait()

    # Simulate travel to bank, entering, and joining line
    print(f"Customer {cid} []: going to bank.")
    door_sem.acquire()
    print(f"Customer {cid} []: entering bank.")
    print(f"Customer {cid} []: getting in line.")

    # Add self to the shared queue
    with queue_lock:
        customer_queue.append(cust)
    queue_sem.release()

    # Wait until a teller selects this customer
    cust.selected_sem.acquire()
    tid = cust.teller_id

    print(f"Customer {cid} []: selecting a teller.")
    print(f"Customer {cid} [Teller {tid}]: selects teller")
    print(f"Customer {cid} [Teller {tid}] introduces itself")

    # Wait for teller to ask for the transaction
    cust.ask_txn_sem.acquire()
    if cust.transaction == "deposit":
        print(f"Customer {cid} [Teller {tid}]: asks for deposit transaction")
    else:
        print(f"Customer {cid} [Teller {tid}]: asks for withdrawal transaction")
    # Tell teller the transaction is given
    cust.txn_given_sem.release()

    # Wait until teller has finished the transaction
    cust.done_sem.acquire()
    print(f"Customer {cid} [Teller {tid}]: leaves teller")
    print(f"Customer {cid} []: goes to door")
    print(f"Customer {cid} []: leaves the bank")

    # Free the door for another customer
    door_sem.release()


def main():
    global closing

    random.seed()  # or set a fixed seed if you want reproducible order

    # Start teller threads
    tellers = []
    for tid in range(NUM_TELLERS):
        t = threading.Thread(target=teller_thread, args=(tid,))
        t.start()
        tellers.append(t)

    # Pre-generate customers and their chosen transactions
    customers = []
    for cid in range(NUM_CUSTOMERS):
        # Randomly choose deposit or withdrawal
        transaction = random.choice(["deposit", "withdrawal"])
        # Print the "wants to perform" lines just like in the sample
        print(f"Customer {cid} []: wants to perform a {transaction} transaction")
        cust = CustomerInfo(cid, transaction)
        customers.append(cust)

    # Start all customer threads
    threads = []
    for cust in customers:
        t = threading.Thread(target=customer_thread, args=(cust,))
        t.start()
        threads.append(t)

    # Wait for all customers to finish
    for t in threads:
        t.join()

    # All customers done -> tellers can go home
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
