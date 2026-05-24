# ML / Deep Learning Skill

## Repo patterns
- Frameworks: TensorFlow/Keras (primary), scikit-learn for classical ML
- Data prep: pandas + numpy, StandardScaler / MinMaxScaler before feeding to nets
- Existing models: CNN (`mnist_cnn.py`), ANN (`mnist_ann.py`), LSTM (`LSTM_Stock/lstm.py`)
- Image classification also in `Classify_Images/cnn.py`

## Non-negotiable practices
- Set random seeds at the top of every training script (`np.random.seed`, `tf.random.set_seed`)
- Always use a validation split during training — never tune on the test set
- Save model weights after training (`model.save()`)
- Plot training history: both loss and the primary metric per epoch
- Print model summary (`model.summary()`) before the training loop

## Architecture decisions
- State input shape and expected output shape in a comment above each layer block
- Document the rationale for major architectural choices (why LSTM vs GRU, why kernel size X)
- For classification: always specify activation + loss together (softmax → categorical_crossentropy, sigmoid → binary_crossentropy)

## Evaluation
- Include a confusion matrix for classification tasks
- Report precision, recall, F1 — not just accuracy
- For regression: report RMSE and MAE alongside R²

## Common pitfalls to flag
- Data leakage: scaling before train/test split
- Class imbalance: check class distribution before training
- Overfitting: compare train vs val loss curves, not just final accuracy
