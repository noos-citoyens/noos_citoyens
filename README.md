# NoOS-citoyens : le code

Ce projet vise à mettre en place un site pour recueillir et analyser les propositions issues d'une consultation citoyenne en écrivant des logiciels libres et en diffusant des données ouvertes anonymisées.
Nous proposerons un ensemble d'outils pour récolter, cartographier, analyser  les propositions.

Il se met en place pendant le mouvement des **Gilets Jaunes**, en concertation avec des associations de manifestants. Notre objectif est de répondre aux besoins d'expression, de dialogue, de compréhension, et ce de façon transparente. 
Le plan n'est pas figé, le code s'écrit au fil des besoins et des évènements, en dialoguant avec les acteurs du mouvement.

Tout citoyen intéressé peut participer à la vie de la plateforme en émettant des propositions, en prenant position pour ou contre les proposition, et en participant à l'analyse des données au travers de campagnes de «crowdsourcing» que nous mettrons en place.

Comme le code, les données récoltées sont diffusées sous licence libre dans des formats ouverts. Toute personne intéressée peut ainsi les télécharger et proposer ses propores analyses.

Toutes les contributions sont les bienvenues, notamment les analyses, enrichissements, visualisation des données. N'hésitez pas à nous contacter pour coopérer ou établir des liens entre les sites utilisant les données récoltées par ces outils.

## Aspects techniques

Pour faciliter les collaborations extérieurs, nous avons choisi de limiter nos choix techniques à des outils bien établis, maîtrisés par de nombreux développeurs. Plonger dans notre code devrait donc être *relativement* facile, du moins on l'espère.

Au lancement, nous avons opté pour:
- un serveur codé en Python avec Flask, 
- des données stockées dans ElasticSearch
- des pages web utilisant ecmascript avec D3.js comme unique dépendance.

Il est difficile de promettre qu'on n'ajoutera aucune autre bibliothèque, mais promis on va tout faire pour se limiter. 

## Installation

Pour nous aider dans le développement, il faut pouvoir lancer une version du serveur en local. 

### Installer l'environement
- cloner ce dépôt
- télécharger et lancer elasticsearch
- créer un virtualenv python et l'activer
- télécharger les dépendances 
`pip install -r requirements.txt`


### Initialiser la BD

Le microframework Flask permet de définir des commandes personnalisées en plus de celle qui lancera le serveur. Nous utilisons ces commandes pour gérer la base de données.

après avoir installé les dépendances avec `pip`, vous devez avoir accès à la commande `flask`, on peut utiliser des variables d'environement pour préciser le module de l'app et le fait qu'on est en mode développement pour activer les options de debug.

Voici le détail des commandes disponibles :

```
noos_citoyens$ FLASK_ENV=development  FLASK_APP=noos  flask --help
Usage: flask [OPTIONS] COMMAND [ARGS]...

  A general utility script for Flask applications.

  Provides commands from Flask, extensions, and the application. Loads the
  application defined in the FLASK_APP environment variable, or from a
  wsgi.py file. Setting the FLASK_ENV environment variable to 'development'
  will enable debug mode.

    $ export FLASK_APP=hello.py
    $ export FLASK_ENV=development
    $ flask run

Options:
  --version  Show the flask version
  --help     Show this message and exit.

Commands:
  clean-es
  init-es
  populate-es
  query-es
  routes       Show the routes for the app.
  run          Runs a development server.
  shell        Runs a shell in the app context.
```

Celles qui nous intéressent le plus : 

Initialiser l'index d'elasticsearch:

`FLASK_ENV=development  FLASK_APP=noos  flask init-es`

Charger un csv de propositions factices pour pouvoir faire des tests : 

(après avoir télécharger le fichier gj-testa.csv)

`FLASK_APP=noos flask populate-es --csv-file gj-testa.csv`


Effacer l'index d'elasticsearch (au cas où)
`FLASK_ENV=development  FLASK_APP=noos  flask clean-es`


Lancer le serveur de dev : 
`FLASK_APP=noos flask run`


### Semantic ui css
Nous avons supprimé l'usage des fonts google qui sont utilisées par default avec semantic-ui.
Seuls les fichiers `dist` sont dans le dépot. 

* edit site.variables

 ```
   /*******************************
         User Global Variables
    *******************************/

    @importGoogleFonts: false;

    @headerFont : 'Open Sans', 'Helvetica Neue', Arial, Helvetica, sans-serif; 
    @pageFont : 'Oswald', 'Helvetica Neue', Arial, Helvetica, sans-serif; 
    @googleFontFamily : 'Open+Sans:400italic,400|Oswald:400,700'; 
```

* gbuild semantic 

   `gulp build`
