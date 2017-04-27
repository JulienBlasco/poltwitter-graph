/**
** BORDER AROUND NODES
*/

    ;(function(undefined) {

  /**
   * Sigma Node Border Custom Renderer
   * ==================================
   *
   * The aim of this simple node renderer is to enable the user to display
   * colored node borders.
   *
   * Author: Guillaume Plique (Yomguithereal)
   * Version: 0.0.1
   */

  sigma.canvas.nodes.border = function(node, context, settings) {
    var prefix = settings('prefix') || '';

    context.fillStyle = node.color || settings('defaultNodeColor');
    context.beginPath();
    context.arc(
     node[prefix + 'x'],
     node[prefix + 'y'],
     node[prefix + 'size'],
     0,
     Math.PI * 2,
     true
    );

    context.closePath();
    context.fill();

    context.lineWidth = node.borderWidth || 1;
    context.strokeStyle = '#fff';
    context.stroke();
  };
}).call(this);

// Add a method to the graph model that returns an
// object with every neighbors of a node inside:
  sigma.classes.graph.addMethod('neighbors', function(nodeId) {
    var k,
        neighbors = {},
        index = this.allNeighborsIndex[nodeId] || {};

    for (k in index)
      neighbors[k] = this.nodesIndex[k];

    return neighbors;
  });

/**
* ON GRAPH LOADING
*/
function implement_clickfunction(s, opacity = "0.2") {
  // We first need to save the original colors of our
  // nodes and edges, like this:
  s.graph.nodes().forEach(function(n) {
    n.color = "rgb(" + [n.r,n.g,n.b].join(",") + ")";
    n.originalColor = n.color;
  });
  s.graph.edges().forEach(function(e) {
    e.color = "rgba(" + [e.r,e.g,e.b,opacity].join(",") + ")";
    e.originalColor = e.color;
  });

  // When a node is clicked, we check for each node
  // if it is a neighbor of the clicked one. If not,
  // we set its color as grey, and else, it takes its
  // original color.
  // We do the same for the edges, and we only keep
  // edges that have both extremities colored.
  s.bind('clickNode', function(e) {
    var nodeId = e.data.node.id,
        toKeep = s.graph.neighbors(nodeId);
    toKeep[nodeId] = e.data.node;

    s.graph.nodes().forEach(function(n) {
      if (toKeep[n.id])
        n.color = n.originalColor;
      else
        n.color = '#eee';
    });

    s.graph.edges().forEach(function(e) {
      if (e.source==nodeId || e.target==nodeId) {
        pieces = e.originalColor.split(",")
        e.color = pieces.slice(0,3).join(",")+",1)";
        }
      else
        e.color = 'rgba(197,197,197,0.1)';
    });
    s.refresh();
  });
  // When the stage is clicked, we just color each
  // node and edge with its original color.
  s.bind('clickStage', function(e) {
    s.graph.nodes().forEach(function(n) {
      n.color = n.originalColor;
    });

    s.graph.edges().forEach(function(e) {
      e.color = e.originalColor;
    });
    s.refresh();
  });
}


function load_graph(s) {
    s.graph.list_of_clusters = [];
    s.graph.nodes().forEach(function(node) {
        node.type = 'border';
        if (!s.graph.list_of_clusters.includes(node.modularity_class)) {
            s.graph.list_of_clusters.push(node.modularity_class)
        }
    });
    s.graph.edges().forEach(function(edge) {
      edge.hidden = true;
    });
    implement_clickfunction(s);
    s.graph.threshold = 0;
    print_pageranks(1-pr_range);
    print_clusters();
}

/**
* GRAPH CUTTING ON SIZE OF NODES
*/

/**
* FUNCTION: ascending( a, b )
*	Comparator function used to sort values in ascending order.
*
* @private
* @param {Number} a
* @param {Number} b
* @returns {Number} difference between `a` and `b`
*/
function ascending( a, b ) {
	return a - b;
} // end FUNCTION ascending()

// QUANTILE //

/**
* FUNCTION: quantile( arr, prob[, opts] )
*	Computes a quantile for a numeric array.
*
* @private
* @param {Array} arr - 1d array
* @param {Number} prob - quantile prob [0,1]
* @param {Object} [opts] - method options:
	`method`: method used to interpolate a quantile value
	`sorted`: boolean flag indicating if the input array is sorted
* @returns {Number} quantile value
*/
function quantile( arr, p, opts ) {
	if ( !Array.isArray( arr ) ) {
		throw new TypeError( 'quantile()::invalid input argument. First argument must be an array.' );
	}
	if ( typeof p !== 'number' || p !== p ) {
		throw new TypeError( 'quantile()::invalid input argument. Quantile probability must be numeric.' );
	}
	if ( p < 0 || p > 1 ) {
		throw new TypeError( 'quantile()::invalid input argument. Quantile probability must be on the interval [0,1].' );
	}
	if ( arguments.length > 2 ) {
		if ( !isObject( opts ) ) {
			throw new TypeError( 'quantile()::invalid input argument. Options must be an object.' );
		}
		if ( opts.hasOwnProperty( 'sorted' ) && typeof opts.sorted !== 'boolean' ) {
			throw new TypeError( 'quantile()::invalid input argument. Sorted flag must be a boolean.' );
		}
		if ( opts.hasOwnProperty( 'method' ) && typeof opts.method !== 'string' ) {
			throw new TypeError( 'quantile()::invalid input argument. Method must be a string.' );
		}
	} else {
		opts = {};
	}
	var len = arr.length,
		id;

	if ( !opts.sorted ) {
		arr = arr.slice();
		arr.sort( ascending );
	}

	// Cases...

	// [0] 0th percentile is the minimum value...
	if ( p === 0.0 ) {
		return arr[ 0 ];
	}
	// [1] 100th percentile is the maximum value...
	if ( p === 1.0 ) {
		return arr[ len-1 ];
	}
	// Calculate the vector index marking the quantile:
	id = ( len*p ) - 1;

	// [2] Is the index an integer?
	if ( id === Math.floor( id ) ) {
		// Value is the average between the value at id and id+1:
		return ( arr[ id ] + arr[ id+1 ] ) / 2.0;
	}
	// [3] Round up to the next index:
	id = Math.ceil( id );
	return arr[ id ];
} // end FUNCTION quantile()


/**
** DISPLAY FUNCTIONS IN VIZ
*/

function print_edges() {
    s.graph.edges().forEach(function(edge) {
      edge.hidden = !(document.forms.display_edges.Checkboxedges.checked);
    });
    s.refresh();
}


function print_nodes() {
    var list_of_clusters = compute_clusters();
    var q = compute_quantile();
    s.graph.nodes_to_display = [];
    s.graph.nodes().forEach(function(node) {
      if (node.pagerank >= q && list_of_clusters.includes(node.modularity_class)){
        node.hidden = false;
      } else {
        node.hidden = true;
        s.graph.nodes_to_display(push(node.id))
      }
    });
}

function print_clusters() {
    var checkedBoxes = document.querySelectorAll('input[name=Checkboxclusters]:checked');
    var list_of_clusters = []
    for (var item of checkedBoxes) {
     list_of_clusters.push(parseInt(item.value))
    }
    if (list_of_clusters.length < s.graph.list_of_clusters.length) {
        s.graph.nodes().forEach(function(node) {
          if (!(list_of_clusters.includes(node.modularity_class))) {
            node.hidden = true;
          }
        });
    } else {
        s.graph.nodes().forEach(function(node) {
          if (list_of_clusters.includes(node.modularity_class)
          && node.pagerank >= s.graph.threshold) {
            node.hidden = false;
          }
        });
    }
    s.graph.list_of_clusters = list_of_clusters;
    s.refresh();
}

function print_pageranks(t) {
    var list_of_pageranks = jQuery.map(s.graph.nodes(), function(element) {
        return element.pagerank;
    });
    var q = quantile(list_of_pageranks, t)
    if (q >= s.graph.threshold) {
        s.graph.nodes().forEach(function(node) {
          if (node.pagerank <= q) {
            node.hidden = true;
          }
        });
    } else {
        s.graph.nodes().forEach(function(node) {
          if (node.pagerank >= q
          && s.graph.list_of_clusters.includes(node.modularity_class)) {
            node.hidden = false;
          }
    });
    }
    s.graph.threshold = q;
    s.refresh();
}

function transparent_edges() {
    s.graph.edges().forEach(function(edge) {
      edge.color = "rgba(192, 192, 192, 0.1)";;
    });
    s.refresh();
}

/***
CHANGE CLUSTERED GRAPH
**/
function change_cluster_stats (cluster) {
    print_clustered_graph(cluster);
    print_clustered_barchart (cluster);
    print_clustered_wordcloud (cluster);
    print_clustered_statistics(cluster);
}

function print_clustered_graph (cluster) {
    s.graph.clear();
    s.refresh();
    s = new sigma();
    s.addRenderer({
      container: 'sigma-container',
      type: 'canvas'
      }
    );

    s.settings('minNodeSize', 0.2);
    s.settings('maxNodeSize', 7);
    s.settings("hideEdgesOnMove", true);
    s.settings("labelThreshold",7);
    graph_data_current_nodes = graph_data.nodes.filter( function(el){
        return el.modularity_class == cluster;
    });
    graph_data_current_pageranks = graph_data_current_nodes.map(n=>n.pagerank);
    q = quantile(graph_data_current_pageranks, 1-pr_range);

    graph_data_current_nodes = graph_data_current_nodes.filter( function(el){
        return el.pagerank >= q;
    });
    graph_data_current_nodes_ids = graph_data_current_nodes.map(n=>n.id);

    graph_data_current = {
        "nodes": graph_data_current_nodes,
        "edges": graph_data.edges.filter( function(el) {
            return graph_data_current_nodes_ids.includes(el.source) &&
                graph_data_current_nodes_ids.includes(el.target);
            })};

    s.graph.read(graph_data_current);
    s.graph.nodes().forEach(function(node) {
        node.type = 'border';
    });
    implement_clickfunction(s, "0.05");
    cl.hide();
    s.refresh();
}

function print_clustered_barchart (cluster) {
    $.getJSON(
    "./barchart_data_" + cluster,
    function(data) {
        myBarChart.chart.config.data = data;
        myBarChart.update();
    });
}

function print_clustered_wordcloud (cluster) {
    cl2.show();
    $.getJSON(
    "./wordcloud_data_" + cluster,
    function(data) {
        var words = data;
        $('#demo').jQCloud('update', data);
        cl2.hide();
    });
}

function print_clustered_statistics(cluster) {
    $.getJSON(
    "/statistics_" + cluster,
    function (data) {
        $("#stats_container").html(
        '<ul class="list-group">'
        + '<li class="list-group-item">Nombre de noeuds : <b>' + data.number_of_nodes + '</b></li>'
        + '<li class="list-group-item">Nombre de liens : <b>' + data.number_of_edges + '</b></li>'
        + '<li class="list-group-item">Degré moyen : <b>' + data.average_degree + '</b></li>'
        + '<li class="list-group-item">Densité de liens : <b>' + data.density + '%</b></li>'
        + '<li class="list-group-item">Taux de clustering moyen : <b>' + data.average_clustering + '%</b></li>'
        + '</ul>'
        );
    });
}