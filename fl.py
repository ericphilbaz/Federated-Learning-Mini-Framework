import argparse

import fed_learn
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-ge", "--global-epochs", help="Number of global (server) epochs", type=int, default=5,
                    required=False)
parser.add_argument("-c", "--clients", help="Number of clients", type=int, default=10, required=False)
parser.add_argument("-d", "--debug", help="Debugging", action="store_true", required=False)
args = parser.parse_args()

nb_clients = args.clients
nb_epochs = args.global_epochs
debug = args.debug


def model_fn():
    return fed_learn.create_model((32, 32, 3), 10)


weight_summarizer = fed_learn.FedAvg()
server = fed_learn.Server(model_fn, nb_clients, weight_summarizer, debug)

for epoch in range(nb_epochs):
    print("Global Epoch {0} is starting".format(epoch))
    server.create_clients()
    server.init_for_new_epoch()

    loss = []

    for client in server.clients:
        print("Client {0} is starting the training".format(client.id))

        server.send_model(client)
        server.send_train_data(client)

        hist = client.edge_train(server.get_client_train_param_dict())
        loss.append(hist.history["loss"])

        server.receive_results(client)

    server.summarize_weights()
    print("Loss (mean): {0}".format(np.mean(loss)))
    print("-" * 30)

    # TODO: test the base model with the aggregated weights
