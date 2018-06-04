import string
import math

def parse_line(line):
    split = line.rstrip().rsplit(None, 1)
    text, category = tuple(split)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = text.translate(str.maketrans("", "", "0123456789"))
    text = text.lower()
    words = text.split()
    return words, category

def build_vocabulary(filename):
    vocabulary = []
    with open(filename) as file:
        for line in file:
            words, _ = parse_line(line)
            vocabulary.extend(words)

    return sorted(set(vocabulary))

def generate_features(input_file, output_file, vocabulary):
    features = []
    with open(input_file) as file:
        for line in file:
            record = {}
            words, category = parse_line(line)
            for word in vocabulary:
                if word in words:
                    record[word] = "1"
                else:
                    record[word] = "0"
            record["classlabel"] = category
            features.append(record)

    with open(output_file, "w") as file:
        file.write(",".join(list(features[0].keys())) + "\n")
        for record in features:
            file.write(",".join(list(record.values())) + "\n")

    return features

def generate_UDPs(features, vocabulary):
    UDPs = {}
    UDPs["1"] = {}
    UDPs["0"] = {}
    true_records = [x for x in features if x["classlabel"] != "0"]
    false_records = [x for x in features if x["classlabel"] == "0"]
    num_true = len(true_records)
    num_false = len(false_records)
    p_class = {}
    p_class["1"] = float(num_true) / float(len(features))
    p_class["0"] = float(num_false) / float(len(features))

    for word in vocabulary:
        UDPs["1"][word] = {}
        matching_records = 0
        for record in true_records:
            if (record[word] == "1"):
                matching_records += 1
        UDPs["1"][word]["1"] = float(matching_records + 1) / float(num_true + 2)
        UDPs["1"][word]["0"] = float(num_true - matching_records + 1) / (num_true + 2)

        UDPs["0"][word] = {}
        matching_records = 0
        for record in false_records:
            if (record[word] == "1"):
                matching_records += 1
        UDPs["0"][word]["1"] = float(matching_records + 1) / (num_false + 2)
        UDPs["0"][word]["0"] = float(num_false - matching_records + 1) / (num_false + 2)

    return UDPs, p_class

def classify(situation, UDPs, p_class):
    predicted = {}
    for class_state in ["0", "1"]:
        predicted[class_state] = math.log(p_class[class_state])
        for word, state in situation.items():
            if word == "classlabel":
                continue
            predicted[class_state] += math.log(UDPs[class_state][word][state])
             
    if predicted["0"] >= predicted["1"]:
        return "0"
    else:
        return "1"

def get_accuracy(data, UDPs, p_class):
    predicted = []
    for situation in data:
        predicted.append(classify(situation, UDPs, p_class))
    actual = [x["classlabel"] for x in data]
    assert len(predicted) == len(actual), "data length mismatch"
    num_correct = 0
    for i in range(len(predicted)):
        if predicted[i] == actual[i]:
            num_correct += 1
    return float(num_correct) / float(len(predicted))

if __name__ == "__main__":
    vocab = build_vocabulary("trainingSet.txt")
    training_data = generate_features("trainingSet.txt", "preprocessed_train.txt", vocab)
    test_data = generate_features("testSet.txt", "preprocessed_test.txt", vocab)
    UDPs, p_class = generate_UDPs(training_data, vocab)
    training_accuracy = get_accuracy(training_data, UDPs, p_class)
    test_accuracy = get_accuracy(test_data, UDPs, p_class)

    print("Trained with: trainingSet.txt")
    print("Tested on:    trainingSet.txt")
    print("Accuracy:     {0}%\n".format(training_accuracy * 100))
    print("Trained with: trainingSet.txt")
    print("Tested on:    testSet.txt")
    print("Accuracy:     {0}%".format(test_accuracy * 100))

    with open("results.txt", "w") as file:
        file.write("Trained with: trainingSet.txt\n")
        file.write("Tested on:    trainingSet.txt\n")
        file.write("Accuracy:     {0}%\n\n".format(training_accuracy * 100))
        file.write("Trained with: trainingSet.txt\n")
        file.write("Tested on:    testSet.txt\n")
        file.write("Accuracy:     {0}%\n".format(test_accuracy * 100))
