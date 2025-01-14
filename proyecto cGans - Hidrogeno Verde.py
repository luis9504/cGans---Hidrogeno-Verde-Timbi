import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras import layers, models

# Datos climáticos históricos de Timbiquí
data = np.array([
    [25.5, 9.6, 5.5],  # [temperatura, velocidad_viento, radiación_solar_aproximada]
    [25.5, 10.2, 5.6],
    [25.9, 9.8, 5.7],
    [26.5, 10.1, 5.8],
    [25.6, 9.5, 5.4],
    [25.2, 9.3, 5.3],
    [25.7, 9.7, 5.6],
    [25.8, 9.8, 5.6],
    [24.4, 8.9, 5.2],
    [25.6, 9.9, 5.5],
    [26.2, 10.3, 5.7],
    [25.6, 9.6, 5.5],
    [24.8, 8.7, 5.1],
    [25.2, 9.2, 5.4],
    [25.9, 9.8, 5.7],
    [24.9, 8.8, 5.3],
    [28.4, 11.1, 6.0],
    [27.0, 10.6, 5.9],
    [27.3, 10.7, 5.9],
    [26.5, 10.2, 5.8],
    [25.9, 9.7, 5.6],
    [26.5, 10.1, 5.8],
    [26.5, 10.0, 5.7],
    [26.5, 10.2, 5.8],
    [27.1, 10.3, 5.8],
    [27.3, 10.4, 5.9],
    [26.2, 10.0, 5.7],
    [27.4, 10.5, 5.9],
    [26.7, 10.1, 5.8],
    [27.0, 10.2, 5.8]
])

# Normalizar los datos
data = (data - data.mean(axis=0)) / data.std(axis=0)

# Dimensiones del modelo
latent_dim = 100
num_features = data.shape[1]

# Generador
def build_generator():
    model = models.Sequential([
        layers.Input(shape=(latent_dim + num_features,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(256, activation='relu'),
        layers.Dense(num_features, activation='linear')
    ])
    return model

# Discriminador
def build_discriminator():
    model = models.Sequential([
        layers.Input(shape=(num_features * 2,)),
        layers.Dense(256, activation='relu'),
        layers.Dense(128, activation='relu'),
        layers.Dense(1, activation='sigmoid')
    ])
    return model

# Construir y compilar modelos
generator = build_generator()
discriminator = build_discriminator()
discriminator.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# CGAN
discriminator.trainable = False
z = layers.Input(shape=(latent_dim,))
condition = layers.Input(shape=(num_features,))
gen_input = layers.Concatenate()([z, condition])
generated_data = generator(gen_input)
disc_input = layers.Concatenate()([generated_data, condition])
validity = discriminator(disc_input)
cgan = models.Model([z, condition], validity)
cgan.compile(optimizer='adam', loss='binary_crossentropy')

# Almacenar las pérdidas y precisión
d_losses = []
g_losses = []
d_accuracies = []

# Entrenamiento de la CGAN
def train(data, epochs=10000, batch_size=32):
    real = np.ones((batch_size, 1))
    fake = np.zeros((batch_size, 1))

    for epoch in range(epochs):
        # Entrenar discriminador
        idx = np.random.randint(0, data.shape[0], batch_size)
        real_data = data[idx]
        noise = np.random.normal(0, 1, (batch_size, latent_dim))
        gen_data = generator.predict(np.hstack([noise, real_data]))
        
        # Entrenar discriminador en datos reales y generados
        d_loss_real = discriminator.train_on_batch(np.hstack([real_data, real_data]), real)
        d_loss_fake = discriminator.train_on_batch(np.hstack([gen_data, real_data]), fake)
        d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

        # Entrenar generador
        g_loss = cgan.train_on_batch([noise, real_data], real)

        # Almacenar métricas
        d_losses.append(d_loss[0])
        g_losses.append(g_loss)
        d_accuracies.append(d_loss[1])

        # Mostrar progreso
        if epoch % 1000 == 0:
            print(f'Epoch {epoch} / {epochs} - D Loss: {d_loss[0]}, D Acc: {d_loss[1]}, G Loss: {g_loss}')

        # Guardar una imagen generada para visualización
        if epoch % 500 == 0:
            plt.figure(figsize=(5, 5))
            plt.plot(data[:, 0], data[:, 1], 'ro', label='Real Data')  # Datos reales para comparación
            plt.plot(gen_data[:, 0], gen_data[:, 1], 'bo', label='Generated Data')  # Datos generados
            plt.title(f'Epoch {epoch}')
            plt.legend()
            plt.savefig(f'generated_epoch_{epoch}.png')
            plt.close()

    # Graficar la evolución de las pérdidas y la precisión
    plt.figure(figsize=(10, 5))

    # Gráfica de pérdidas
    plt.subplot(1, 2, 1)
    plt.plot(d_losses, label='D Loss')
    plt.plot(g_losses, label='G Loss')
    plt.title('Losses During Training')
    plt.legend()

    # Gráfica de precisión del discriminador
    plt.subplot(1, 2, 2)
    plt.plot(d_accuracies, label='D Accuracy')
    plt.title('Discriminator Accuracy')
    plt.legend()

    plt.tight_layout()
    plt.savefig('training_metrics.png')
    plt.show()

# Ejecutar entrenamiento
train(data, epochs=5000)
