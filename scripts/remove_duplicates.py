# Date: 05/09/2019
# Author: Mohamed
# Description: Remove duplicates

import os
import hashlib
from threading import Thread


class RemoveDuplicates:

    def __init__(self, trainset_dir, validset_dir):
        self.trainset_dir = trainset_dir
        self.validset_dir = validset_dir

        self.trainset_data = {}
        self.validset_data = {}

        self.duplicates_remove = 0

    def get_fingerprint(self, img):
        with open(img, 'rb') as f:
            content = f.read()

        return hashlib.sha256(content).hexdigest()

    def set_train_data(self):
        print('\nSetting training data ...')
        for root, _, files in os.walk(self.trainset_dir):

            for filename in files:
                img = os.path.join(root, filename)
                fingerprint = self.get_fingerprint(img)

                if fingerprint in self.trainset_data:
                    self.duplicates_remove += 1
                    os.remove(img)
                    continue

                self.trainset_data[fingerprint] = img

    def set_valid_data(self):
        print('\nSetting validation data ...')
        for root, _, files in os.walk(self.validset_dir):

            for filename in files:
                img = os.path.join(root, filename)
                fingerprint = self.get_fingerprint(img)

                if fingerprint in self.validset_data:
                    self.duplicates_remove += 1
                    os.remove(img)
                    continue

                self.validset_data[fingerprint] = img

    def remove_dupilcates(self):
        print('\nRemoving dupilcates ...')
        for fingerprint in self.trainset_data:

            if fingerprint in self.validset_data:
                self.duplicates_remove += 1
                os.remove(self.trainset_data[fingerprint])

    def start(self):
        t1 = Thread(target=self.set_train_data, daemon=True)
        t2 = Thread(target=self.set_valid_data, daemon=True)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        self.remove_dupilcates()

        print('Removed {} duplicates'.format(
            self.duplicates_remove
        ))


if __name__ == '__main__':
    trainset_dir = '../ai/dataset/train/dogs/'
    validset_dir = '../ai/dataset/valid/dogs/'

    remove_duplicates = RemoveDuplicates(trainset_dir, validset_dir)
    remove_duplicates.start()
