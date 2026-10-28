# Contexte d'entreprise — pourquoi ce projet existe

Ce document ancre le projet dans une **réalité d'entreprise** : le problème concret qu'il résout, la mission qu'il incarne, et la valeur qu'il apporte.

## 🏢 L'entreprise : NovaPay

NovaPay édite une application SaaS de gestion de paiements pour des commerçants. ~35 développeurs, l'application est livrée **plusieurs fois par jour** (déploiement continu). L'équipe sécurité ne compte que 2 personnes.

## ⚠️ Le problème

La sécurité est un **contrôle manuel en fin de cycle** : un audit prestataire une fois par trimestre. Entre deux audits, tout passe. En 6 mois, trois incidents :

1. **Dépendance vulnérable en production** — une vieille librairie avec une CVE critique (type Log4Shell) est restée en prod des semaines, arrivée par une mise à jour automatique. Personne ne l'avait vue.
2. **Secret en dur poussé sur Git** — un token d'API laissé dans le code, désormais dans l'historique du dépôt.
3. **Audit client raté** — une banque cliente exige la preuve que NovaPay scanne code et conteneurs **à chaque livraison**. Aucune preuve disponible → contrat suspendu.

**Le constat :** détecter les failles manuellement, après coup, ne tient pas quand on livre 10 fois par jour.

## 🎯 La mission (rôle DevSecOps)

> « Fais en sorte qu'un code ou une image vulnérable ne puisse plus jamais atteindre la production — automatiquement, sans ralentir les développeurs. »

C'est le principe du **shift-left** : la sécurité **dans** le pipeline, pas à côté.

## 🔗 Comment le projet résout chaque problème

| Problème vécu par NovaPay | Mécanisme du pipeline | Résultat |
|---|---|---|
| Dépendance vulnérable en prod | Trivy (SCA) scanne les dépendances à chaque build | CVE détectée → livraison **bloquée** |
| Secret en dur sur Git | SonarQube (SAST) + Quality Gate | Commit **refusé** avant le merge |
| Image conteneur obsolète | Trivy image scanne l'image de base | Image vulnérable **non déployée** |
| Audit « prouvez que vous scannez » | Rapports de scan archivés à chaque run | Preuve **automatique et horodatée** |
| Sécurité = goulot manuel | Tout automatisé dans Jenkins | Les devs livrent vite **et** en sécurité |

La **démo avant / après** (pipeline rouge → vert) est la démonstration vivante : une faille est bloquée, puis sa correction débloque la livraison.

## 💼 Valeur professionnelle

Le DevSecOps est l'une des compétences les plus recherchées en 2026. Ce projet démontre la capacité à :
- intégrer la sécurité dans une chaîne CI/CD réelle (Jenkins) ;
- manier les outils standards du marché (SonarQube, Trivy) ;
- **raisonner en risque métier**, pas seulement en technique — la marque d'un futur architecte sécurité.

**En entretien :** non pas « j'ai fait un pipeline Jenkins », mais « j'ai mis en place une chaîne qui empêche automatiquement une dépendance vulnérable ou un secret d'atteindre la production — le genre d'incident qui coûte un client à une entreprise comme NovaPay ».
