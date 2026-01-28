# Résumé du Projet : Détection d'Anomalies par Système Multi-Agents

> **Cours :** Intelligence Artificielle Distribuée (SDA 2024)
> **Statut :** Version 3.0 (Grade Industriel)

## 1. Le Problème
Dans les grands systèmes industriels ou l'Internet des Objets (IoT), il y a des milliers de capteurs. Envoyer toutes les données vers un serveur central pose problème :
*   **Surcharge** : Trop de données saturent le réseau.
*   **Lenteur** : Le temps d'aller-retour retarde la détection des pannes.
*   **Fragilité** : Si le serveur central tombe en panne, plus rien ne marche.

## 2. Notre Solution : L'IA Distribuée
Au lieu d'un "Serveur Roi", nous utilisons une **approche décentralisée**. Nous déployons des **Agents Intelligents** (des petits programmes autonomes) directement sur chaque capteur.

L'intelligence est déplacée **vers la périphérie (Edge AI)**.

## 3. Comment ça marche ? (Les 3 Étapes)

### Étape 1 : Détection Locale (Streaming O(1))
Chaque agent surveille ses propres données en temps réel. Il utilise un algorithme d'apprentissage en ligne ultra-rapide (**River Half-Space Trees**) qui apprend en continu sans stocker d'historique (complexité constante).

### Étape 2 : Discussion (Le "Vote")
Si un agent voit quelque chose de bizarre, il ne panique pas. Il contacte ses voisins pour demander : *"Est-ce que vous voyez ça aussi ?"*.
*   Si c'est juste du bruit sur un seul capteur, les voisins répondent "Non". L'alerte est annulée.
*   Si c'est une vraie panne générale, les voisins répondent "Oui".

### Étape 3 : Confiance et Auto-Réparation (La "Sagesse")
C'est la partie avancée de notre projet (Version 3.0) :
*   **Système de Confiance** : Les agents notent leurs voisins. Si un capteur crie au loup trop souvent, sa note baisse.
*   **Heartbeat (Pouls)** : Les agents s'envoient des "bips" réguliers. Si un voisin ne répond plus, il est considéré comme mort et déconnecté automatiquement.

## 4. Résultats Obtenus
Nous avons simulé ce système avec succès :
*   **Fiabilité** : Nous détectons **>91%** des vraies anomalies majeures.
*   **Précision** : Grâce à l'apprentissage en ligne, nous avons atteint notre record de précision (**62.4%**).
*   **Robustesse** : Le système s'auto-répare en cas de panne d'agent grâce aux Heartbeats.

## 5. Conclusion
Ce projet démontre qu'une "armée" de petits agents intelligents collaboratifs est plus efficace et robuste qu'un gros serveur central pour surveiller des infrastructures critiques.
