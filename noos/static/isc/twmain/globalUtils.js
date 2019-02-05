
// ajax request
// args:
//   - type:     REST method to use: GET (by def), POST...
//   - url:      target url
//   - data:     url params or payload if POST
//   - datatype: expected response format: 'json', 'text' (by def)...
var AjaxSync = function(args) {

    if (!args)                        args = {}
    if (isUndef(args.url))            console.error("AjaxSync call needs url")
    if (isUndef(args.type))           args.type = 'GET'
    if (isUndef(args.datatype))       args.datatype = 'text'
    else if (args.datatype=="jsonp")  args.datatype = "json"

    // will contain success bool, format and data itself
    var Result = []

    // format will influence downstream parser choice
    var format = null ;

    if (TW.conf.debug.logFetchers)
      console.log("---AjaxSync---", args)

    // use file extension to guess expected format (headers are more variable)
    if (args.url && args.url.length) {
      let extMatch = args.url.match(/\.(gexf|json)$/)
      if (extMatch) {
        format = extMatch.pop()
        if (TW.conf.debug.logFetchers)
          console.info(`before AjaxSync(${args.url}): format is ${format}, according to file extension`);
      }
    }

    $.ajax({
            type: args.type,
            url: args.url,
            dataType: args.datatype,
            async: false,  // <= synchronous (POSS alternative: cb + waiting display)

            // our payload: filters...
            data: args.data,
            contentType: 'application/json',
            success : function(data, textStatus, jqXHR) {
              // header checked iff format not apparent from extension
              if (format == null) {
                var header = jqXHR.getResponseHeader("Content-Type")
                if (header &&
                     (header == "application/json"
                      || header == "text/json")
                  ) {
                    format = "json" ;
                  }
                else {
                  // default parser choice if xml or if undetailed header
                  format = "gexf" ;
                  if (TW.conf.debug.logFetchers)
                    console.debug("after AjaxSync("+args.url+") => response header="+header +"not json => fallback on xml gexf");
                }
              }
              Result = { "OK":true , "format":format , "data":data };
            },
            error: function(exception) {
              console.warn('ajax error:', exception, exception.getAllResponseHeaders())
              Result = { "OK":false , "format":false , "data":exception.status };
            }
        });
    return Result;
}

function compareNumbers(a, b) {
    return a - b;
}

function isNumeric(a) {
    return parseFloat(a) == a ;
}

//python range(a,b) | range(a)
function calc_range(begin, end) {
  if (typeof end === "undefined") {
    end = begin; begin = 0;
  }
  var result = [], modifier = end > begin ? 1 : -1;
  for ( var i = 0; i <= Math.abs(end - begin); i++ ) {
    result.push(begin + i * modifier);
  }
  return result;
}

function isUndef(variable){
    if(typeof(variable)==="undefined") return true;
    else return false;
}


function stringToSomeInt (anyString) {
  let charCodeSum = 0
  if (anyString && anyString.length) {
    for (let i = 0 ; i < anyString.length ; i++) {
      charCodeSum += anyString.charCodeAt(i)
    }
  }
  return charCodeSum
}

// shuffle algo from stackoverflow.com/a/6274398/2489184
function shuffle(array) {
    var counter = array.length;

    // While there are elements in the array
    while (counter > 0) {
        // Pick a random index
        let index = Math.floor(Math.random() * counter);

        // Decrease counter by 1
        counter--;

        // And swap the last element with it
        let temp = array[counter];
        array[counter] = array[index];
        array[index] = temp;
    }

    return array;
}

getUrlParam = (function () {
    var get = {
        push:function (key,value){
            var cur = this[key];
            if (cur.isArray){
                this[key].push(value);
            }else {
                this[key] = [];
                this[key].push(cur);
                this[key].push(value);
            }
        }
    },
    decode = function (s, rmSpaceFlag) {
        s = decodeURIComponent(s.replace(/\+/g, ' '));
        return rmSpaceFlag ? s.replace(/\s+/g,'') : s;
    };
    document.location.search.replace(
               /\??(?:([^=]+)=(?:%22(.*?)%22|"([^"]*)"|([^&]*))&?)/g,
            //        ^^^^^^^       ^^^^^   | ^^^^^^^ |^^^^^^^
            //          key     valUrlquoted|valQuoted|valRaw
            //  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            //                       wholeMatch

            function (wholeMatch,key,valUrlquoted,valQuoted,valRaw) {

        // exemple
        // -------
        // wholeMatch:      ?type=%22filter%22&
        // key:             type
        // valUrlquoted:    filter

        // debug
        // -----
        // console.log("getUrlParam re vars wholeMatch  :", wholeMatch)
        // console.log("getUrlParam re vars key         :", key)
        // console.log("getUrlParam re vars valUrlquoted:", valUrlquoted)
        // console.log("getUrlParam re vars valQuoted   :", valQuoted)
        // console.log("getUrlParam re vars valRaw      :", valRaw)

        var val = ""
        if (typeof valUrlquoted != "undefined") {
            val = valUrlquoted
        }
        else if (typeof valQuoted != "undefined") {
            val = valQuoted
        }
        else {
            val = valRaw
        }

        if (get[decode(key,true)]){
            get.push(decode(key,true),decode(val));
        }else {
            get[decode(key,true)] = decode(val);
        }

        // debug
        // -----
        // console.log("getUrlParam output dict:\n  ", JSON.stringify(get))

    });
    return get;
})();



function ArraySortByValue(array, sortFunc){
    var tmp = [];
    for (var k in array) {
      tmp.push({
          key: k,
          value:  array[k]
      });
    }

    // reverse numeric on prop 'value'
    tmp.sort(function(o1, o2) {
        return (parseFloat(o2.value) - parseFloat(o1.value));
    });
    return tmp;
}

// Sorts by 2 keys and creates an agregated weight
//  key1: how many times the node appears as neighbor
//  key2: cumulated weight of all edges
//  output value:   coef x key1 + key2
//  with coef > Max(key2) to preserve the order
//
//  ex input {"kw1":[2,10], "kw2":[2,3], "kw3":[5,4]}
//     - the expected output order is kw3, kw1, kw2
//     - max key2 is 10
//       => we set coef to 10+1 to allow key1 to always dominate key2 influence
//     - the result sorted array with agregated values for proportional labels
//       will be: [
//                  [key: kw3, value: 59],   <--- 5*coef +  4
//                  [key: kw1, value: 32],   <--- 2*coef + 10
//                  [key: kw2, value: 25]    <--- 2*coef +  3
//                ]
// NB the output agregated values 59, 32, 25 are used for htmlProportionalLabels
function ArraySortByAgValueIndepOccsPlusWeight(array, sortFunc){
    let maxWeiSum = 0
    for (var nid in array) {
      var [indepOccs, weiSum] = array[nid]
      weiSum = parseFloat(weiSum)
      if (weiSum > maxWeiSum) {
        maxWeiSum = weiSum
      }
    }

    let coef = Math.ceil(maxWeiSum) + 1

    let arrayWithAgregatedVals = {}
    for (var nid in array) {
      var [indepOccs, weiSum] = array[nid]
      indepOccs = parseFloat(indepOccs)
      weiSum    = parseFloat(weiSum)
      arrayWithAgregatedVals[nid] = coef * indepOccs + weiSum
    }
    return ArraySortByValue(arrayWithAgregatedVals, sortFunc)
}


function getByID(elem) {
    return document.getElementById(elem);
}

// NB: check if we could use sigma.plugins.animate.parseColor instead
// hex can be RGB (3 or 6 chars after #) or RGBA (4 or 8 chars)
function hex2rgba(sent_hex) {
    if (!sent_hex) {
      return [0,0,0,1]
    }
    result = []
    hex = ( sent_hex.charAt(0) === "#" ? sent_hex.substr(1) : sent_hex );
    // check if 6 letters are provided
    if (hex.length == 6 || hex.length == 8) {
        result = calculateFull(hex);
        return result;
    }
    else if (hex.length == 3 || hex.length == 3) {
        result = calculatePartial(hex);
        return result;
    }
}

function calculateFull(hex) {
    var r = parseInt(hex.substring(0, 2), 16);
    var g = parseInt(hex.substring(2, 4), 16);
    var b = parseInt(hex.substring(4, 6), 16);

    var a = 0
    if (hex.substring(6, 8)) {
      a = parseInt(hex.substring(6, 8), 16) / 255;
    }
    return [r,g,b, a];
}


// function for calculating 3 letters hex value
function calculatePartial(hex) {
    var r = parseInt(hex.substring(0, 1) + hex.substring(0, 1), 16);
    var g = parseInt(hex.substring(1, 2) + hex.substring(1, 2), 16);
    var b = parseInt(hex.substring(2, 3) + hex.substring(2, 3), 16);
    var a = 0
    if (hex.substring(3, 4)) {
      a = parseInt(hex.substring(3, 4), 16) / 255;
    }

    return [r,g,b, a];
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

// high-level hex or rgba color format to rgb string => for example "255,32,255"
function normalizeColorFormat(colStr) {
  let rgbStr = null
  let rgbaVals = []
  let invalidFormat = false

  if (typeof colStr == 'undefined' || ! colStr) {
    invalidFormat = true
  }
  // hex color ex "#eee or #AA00AA"
  else if (/^#[A-Fa-f0-9]{3,6}$/.test(colStr)) {
    rgbaVals = hex2rgba(colStr)
    rgbStr = rgbaVals.splice(0, 3).join(',');
  }
  else {
    // "rgba(...)" or "rgb(...)" color
    if (/^rgba?\(\d{1,3},\d{1,3},\d{1,3}(?:,\d{1,3})?\)$/.test(colStr)) {
      // keep only the inside of parens (ex: "255,32,255,100")
      colStr = colStr.match(/rgba?\(([^)]+)\)/)[1]
      rgbaVals = colStr.split(',')
    }
    // we also allow data providing directly the inside (ex: "255,32,255,100")
    else if (/^\d{1,3},\d{1,3},\d{1,3}(?:,\d{1,3})?$/.test(colStr)) {
      rgbaVals = colStr.split(',')
    }

    if (rgbaVals.length == 3) {
      rgbStr = colStr
    }
    else if (rgbaVals.length == 4) {
      rgbStr = rgbaVals.splice(0, 3).join(',');
    }
    else {
      invalidFormat = true
    }

  }

  if (invalidFormat) {
    rgbStr = null
  }

  return rgbStr
}

// light or dark color => true or false
function colorIsLight (aColor) {
  let rgbCol = normalizeColorFormat(aColor).split(/,/)
  let lightness = parseInt(rgbCol[0]) + parseInt(rgbCol[1]) + parseInt(rgbCol[2])
  // 382 = (255 * 3) / 2
  return Boolean(lightness > 382)
}


// lowercase etc query strings
normalizeString = function(string, escapeHtml) {
    if (typeof escapeHtml == "undefined") {
        escapeHtml = true ;
    }
    if (! typeof string == "string") {
        return "" ;
    }
    else {
        string = $.trim( string.toLowerCase() )
        if (escapeHtml == true) {
            string = saferString(string) ;
        }
        return string ;
    }
}

// html-escape user-input strings (before printing them out)
// (or use jquery .text())
saferString = function(string) {
    // TODO table in an outer scope
    conversions = {
        '&' : '&amp;'   ,
        '<' : '&lt;'    ,
        '>' : '&gt;'    ,
        '"' : '&quot;'  ,
        "'" : '&apos;'  ,
        "{" : '&lcub;'  ,
        "}" : '&rcub;'  ,
        '%' : '&percnt;'
    } ;

    matchables = /[&<>"'{}%]/g ;

    if (! typeof string == "string") {
        return "" ;
    }
    else {
        return string.replace(
            matchables,
            function(char) {
                return conversions[char]
            }
        )
    }
}


 /**
  * function to test if file exists
  * via XHR, enhanced from http://stackoverflow.com/questions/5115141
  */

var linkCheck = function(url) {
    var http = new XMLHttpRequest();
    try {
      http.open('HEAD', url, false);  // 3rd arg false <=> synchronous request
      http.send();
      return http.status!=404;
    }
    catch(e) {
      return false
    }
}

 /**
  * function to load a given css file
  * cf. activateModules()
  */
 loadCSS = function(href) {
     var cssLink = $("<link rel='stylesheet' type='text/css' href='"+href+"'>");
     $("head").append(cssLink);
 };

/**
 * function to load a given js file
 * cf. activateModules()
 */
 loadJS = function(src) {
     var jsLink = $("<script type='text/javascript' src='"+src+"'>");
     $("head").append(jsLink);
 };
