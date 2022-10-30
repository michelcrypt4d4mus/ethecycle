from ethecycle.blockchains.ethereum import Ethereum

i = 0
found_bridges = False
found_multisig = False

with open('data/wallet_labels/ethereum.txt', 'r') as file:
    with open('data/wallet_labels/ethereum_new.txt', 'a') as write_file:
        for line in file:
            line = line.rstrip()
            if line.startswith('# Bridges'):
                #print("Found Bridges start;")
                found_bridges = True
            elif line.startswith('# multisig'):
                found_multisig = True
            if found_bridges or line.startswith('# ') or line.startswith('0x') and ' ' not in line:
                print(line)
                continue
            else:
                print(line)
                if found_multisig:
                    print('multisig')
                else:
                    print('cex')
