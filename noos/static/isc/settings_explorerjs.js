'use strict;'

var TW = {}

TW.conf = (function(TW){

  let TWConf = {}

  TWConf.branding = {
    'name': 'NOos-citoyens',   // <--- name displayed in upper left
    'link': 'http://noos-citoyens.fr',                         // home  link
    'video': 'https://player.vimeo.com/video/38383946'  // video link
  }

  // ==========================
  // TINA POSSIBLE DATA SOURCES
  // ==========================

  // Graph data source
  // -----------------
  // the graph input depends on TWConf.sourcemode (or manual url arg 'sourcemode')
  TWConf.sourcemode = "servermenu"   // accepted: "api" | "serverfile" | "servermenu" | "localfile"

  // ...or remote bridge to default source api ajax queries
  TWConf.sourceAPI={}
  TWConf.sourceAPI["nodetypes"] = {"node0": "Keywords", "node1": "Scholars" }
  TWConf.sourceAPI["forNormalQuery"] = "services/api/graph"
  TWConf.sourceAPI["forFilteredQuery"] = "services/api/graph"


  // Related documents (topPapers) data source
  // -----------------------------------------

  TWConf.getRelatedDocs = true
  TWConf.relatedDocsMax = 100

  // fallback type (if no detailed source-by-source conf from db.json)
  TWConf.relatedDocsType = "csv"          // accepted: "twitter" | "csv" | "CortextDB"
                                          // POSSible: "elastic"

  // routes by corresponding type
  TWConf.relatedDocsAPIS = {
    "twitter": "/twitter_search",
    "CortextDB": "twbackends/phpAPI",
    "csv": "https://noos-citoyens.fr"
//    "csv": "twbackends/phpAPI"
  }

  // fallback topPapers API if none found by type
  //TWConf.relatedDocsAPI = "http://localhost:5000"
  TWConf.relatedDocsAPI = "twbackends/phpAPI"
	
  // =======================
  // DATA FACETS AND LEGENDS
  // =======================
  // to process node attributes values from data
  //    => colors   (continuous numeric attributes)
  //    => clusters (discrete numeric or str attributes)

  // cf. also "Configuring facets" in the doc under Introduction/project_config

  // create facets ?
  TWConf.scanAttributes = true

  // use a facet for default color
  TWConf.defaultColoring = "clust_louvain"

  // facetOptions: choose here the default visual result of your node attributes
  // ---------------------------------------------------------------------------
  // (values overridden by data/myproject/project_conf.json "facets" if present)
  TWConf.defaultFacetOptions = {

    // attr title          coloring fun       nbins       binning strategy       label in menus
    'auto-size'       : {'col': "gradient", 'n': 6,  'binmode': 'samerange', 'legend': 'Auto Size'  },
    'auto-degree'     : {'col': "heatmap",  'n': 7,  'binmode': 'samepop',   'legend': 'Auto Degree'},
    'auto-indegree'   : {'col': "heatmap",  'n': 7,  'binmode': 'samepop', 'legend': 'Auto InDegree'},
    'auto-outdegree'  : {'col': "heatmap",  'n': 7,  'binmode': 'samepop', 'legend': 'Auto OutDegree'},
    'cluster_index'   : {'col': "cluster" ,          'binmode': 'off'        },
    'clust_louvain'   : {'col': "cluster" ,          'binmode': 'off',
                         'legend':'Louvain clustering', 'titlingMetric': 'auto-size'},
    'country':{
                         'col':"cluster" ,
                         'binmode': 'off',
                         'legend': 'Country',
                         'titlingMetric': 'off'
              },
    'total_occurrences':{
                         'col':"heatmap" ,
                         'binmode': 'samerange',
                         'n': 3,
                         'legend': 'Total occurrences'
                       }
  }
  // NB  automatic cases with no binning:
  //     - if data type is not numeric
  //     - if there is less than distinct values that maxDiscreteValues

  // NB for heatmapColoring:
  //     - if number of bins is even, the 2 classes in the middle get white
  //     - the maximum number of bins is 24

  // when coloring method is "cluster", should the colors change each time ?
  TWConf.randomizeClusterColors = true

  // default clustering attribute (<---> used for initial node colors)
  TWConf.nodeClusAtt = "modularity_class"

  // for binning decision and nbins (fallbacks if attr is not in facetOptions)
  TWConf.maxDiscreteValues = 15
  TWConf.legendsBins = 7

  // to normalize node sizes (larger range max-min increases visual size difference)
  //                         (larger min           increases overall visual size)
  TWConf.desirableNodeSizeMin=4000;
  TWConf.desirableNodeSizeMax=5010;


  // =============
  // TINA BEHAVIOR
  // =============

  // Node typology: categories (resp. 0 and 1) will get these default labels
  TWConf.catSem = "Thème";
  TWConf.catSoc = "Expression";
  // NB: these labels may be superseded by:
  //   - the input data's node types values cf. sortNodeTypes()
  //   - in project_conf.md the node0 & node1 properties

  // Modules path
  // ------------
  TWConf.paths = {
    'ourlibs':   'twlibs',
    'modules':   'twmodules',
    'templates': 'twlibs/default_hit_templates',   // some default templates

    'sourceFile': null,              // server: 1 default gexf|json graph source
    'sourceMenu': "static/isc/server_menu.json" // ...or server: a gexf|json sources list
  }

  // Active modules
  // --------------
  TWConf.ModulesFlags = {} ;
  // flag name is div class to be removed if false
  //        *and* subdirectory of modules path to import if true
  // see also activateModules()
  TWConf.ModulesFlags["multivacV1HistogramModule"] = false ;

  // cf. twmodules/multivacV2HistogramModule/multivacV2Settings.js for settings
  TWConf.ModulesFlags["multivacV2HistogramModule"] = false ;

  // cf. twmodules/crowdsourcingModule/README.md to initialize the associated db
  TWConf.ModulesFlags["crowdsourcingModule"] = true ;

  // create the automated exploration instance (in 'demo' var)
  TWConf.ModulesFlags["demoFSAModule"] = false ;

  // Other GUI options
  // ------------------
  TWConf.sidePanelSize = "450px"       // width of the side panel (def: 400px)

  TWConf.filterSliders = true          // show sliders for nodes/edges subsets

  TWConf.colorByAtt = true;            // show "Set colors" menu

  TWConf.tuningPanel = false;           // show "Tune settings" menu button

  TWConf.dragNodesAvailable = true;    // allow dragging nodes with CTRL+click

  TWConf.deselectOnClickStage = false   // click on background remove selection?
                                        // (except when dragging)
  TWConf.deselectOnDoubleClickStage = true   // idem double click on background

  TWConf.histogramStartThreshold = 1000 ;   // for daily histo module
                                          // (from how many docs are significant)


  // £TODO these exist only in git branches
  //       (geomap: ademe, timeline: tweetoscope)
  //       ==> ask if need to be restored
  // TW.geomap = false;
  // TW.twittertimeline = false;

  TWConf.maxPastStates = 15 ;      // number of TW.states to remember (~CTRL-Z)


  // Layout options
  // --------------
  TWConf.disperseAvailable=false;   // show/hide disperseButton
  TWConf.fa2Available=false;        // show/hide fa2Button

  // if fa2Available, the auto-run config:

    TWConf.fa2Enabled= false;        // fa2 auto-run at start and after graph modified ?
    TWConf.fa2Milliseconds=900;     // constant factor in duration of auto-run
    TWConf.fa2AdaptDuration=true;   // duration of auto-run proportional log(nEdges)
    TWConf.minNodesForAutoFA2 = 5   // graph size threshold to auto-run
    TWConf.fa2SlowerMeso = true     // slow down meso if few nodes


  // Full-text search
  // ----------------
  TWConf.maxSearchResults = 100            // how many "top papers" to display
  TWConf.minLengthAutoComplete = 2        // how many chars to type for autocomp
  TWConf.maxSuggestionsAutoComplete = 10  // how many suggestions by autocomp
  TWConf.strSearchBar = "Select topics"


  // ===================
  // RENDERING SETTINGS
  // ===================
  TWConf.twRendering = true ;     // false: use sigma "stock" rendering
                                  // true:  use our rendering customizations
                                  //        (nodes with borders,
                                  //         edges with curves,
                                  //         better labels, etc)

  TWConf.overSampling = true      // hi-def rendering (true => pixelRatio x 2)
                                  // (/!\ costly)

  TWConf.stablePositions = true    // remember overall positions for all types
                                   //    (and when layouts are called,
                                   //     all types are moving together
                                   //      even when some are hidden)

  TWConf.independantTypes = true   // if stablePositions, types are not moving together

  TWConf.colorTheme = "24DivergingZeileis"   // color palette for clusters
                                             //  - "9CBrewerSet1"
                                             //  - "12CBrewerPaired",
                                             //  - "22Kelly"
                                             //  - "24DivergingZeileis"
                                             //  - "24ContrastedPastel"
                                             //  - "50Fluo"
                                             //  - "50Pastel"
                                             //  - "80Pastel"
                                             //  - "128Tina"

  // sigma rendering settings
  // ------------------------
  TWConf.sigmaJsDrawingProperties = {
      // nodes
      defaultNodeColor: "#ddd",
      twNodeRendBorderSize: 1,           // node borders (only iff ourRendering)
      twNodeRendBorderColor: "#222",

      // edges
      minEdgeSize: 1,                    // in fact used in tina as edge size
      defaultEdgeType: 'curve',          // 'curve' or 'line' (curve only iff ourRendering)
      twEdgeDefaultOpacity: 0.4,         // initial opacity added to src/tgt colors

      // labels
      font: "Droid Sans",                // font params
      fontStyle: "bold",
      defaultLabelColor: '#000',         // labels text color
      labelSizeRatio: 1,                 // label size in ratio of node size
      labelThreshold: 4,                 // min node cam size to start showing label
                                         // (old tina: showLabelsIfZoom)

      // hovered nodes
      // -------------
      twDefaultBGBoxColor: '#fff',      // common value for hovered/selected
                                        //               label box bg def color
      defaultHoverLabelColor: '#000',
      borderSize: 2.5,                   // for ex, bigger border when hover
      nodeBorderColor: "node",           // choices: 'default' color vs. node color
      defaultNodeBorderColor: "black",   // <- if nodeBorderColor = 'default'
      labelHoverBGColor: "default",     // "node" for a label bg like the node color,
                                        // "default" for a bg with defaultBGBoxColor

      // selected nodes
      // --------------
      twSelectedBGColor: "default",     // "node" for a label bg like the node color,
                                        // "default" for a bg with defaultBGBoxColor

      // not selected <=> (1-greyness)
      twNodesGreyOpacity: .5,                       // smaller value: more grey
      twBorderGreyColor: "rgba(100, 100, 100, 0.5)",
      twEdgeGreyColor: "rgba(100, 100, 100, 0.25)",
  };
  // NB: sigmaJsDrawingProperties are available as 'settings' in all renderers
  // cf. https://github.com/jacomyal/sigma.js/wiki/Settings#renderers-settings


  // tina environment rendering settings
  // -----------------------------------
  // normal and meso level background colors
  TWConf.normalBackground = '#fff'             // <= should match css default
  TWConf.mesoBackground = '#fcfcd5'

  // mouse captor zoom limits
  TWConf.zoomMin = 1/64            // for zoom IN   (ex: 1/64 to allow zoom x64)
  TWConf.zoomMax = 8               // for zoom OUT

  // NB these "inverted" semantics are based on sigma's own zoomMin and zoomMax
  //    cf. https://github.com/jacomyal/sigma.js/wiki/Settings#captors-settings

  // circle selection cursor
  TWConf.circleSizeMin = 10;
  TWConf.circleSizeMax = 200;
  TWConf.moreLabelsUnderArea = true; // show 3x more labels under area (/!\ costly)

  // em size range for neighbor nodes "tagcloud"  (1 = "normal size")
  TWConf.tagcloudFontsizeMin = .8  ;
  TWConf.tagcloudFontsizeMax = 2 ;

  TWConf.tagcloudSameLimit = 50     // max displayed neighbors of the same type
  TWConf.tagcloudOpposLimit = 50    // max displayed neighbors of the opposite type

  // relative sizes (iff ChangeType == both nodetypes)
  TWConf.sizeMult = [];
  TWConf.sizeMult[0] = 2.0;     // ie for node type 0 (<=> sem)
  TWConf.sizeMult[1] = 2.0;     // ie for node type 1 (<=> soc)


  // ===========
  // DEBUG FLAGS
  // ===========
  TWConf.debug = {
    initialShowAll: false,           // show all nodes on bipartite case init (docs + terms in one view)

    // show verbose console logs...
    logFetchers: false,              // ...about ajax/fetching of graph data
    logParsers: false,               // ...about parsing said data
    logFacets: false,                // ...about parsing node attribute:value facets
    logSettings: false,              // ...about settings at Tina and Sigma init time
    logStates: false,                // ...about TW.states array
    logSelections: false
  }

  Object.freeze(TWConf.paths)  // /!\ to prevent path modification before load
  Object.freeze(TWConf.branding)  // idem

  return TWConf
})()

console.log("TW.conf load OK")
