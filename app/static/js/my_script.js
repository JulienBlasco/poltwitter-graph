/**
* ON GRAPH LOADING
*/
function implement_clickfunction(s) {
      // We first need to save the original colors of our
      // nodes and edges, like this:
      s.graph.nodes().forEach(function(n) {
        n.originalColor = n.color;
      });
      s.graph.edges().forEach(function(e) {
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
          if (e.source==nodeId || e.target==nodeId)
            e.color = e.originalColor;
          else
            e.color = '#eee';
        });
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
  });
}


function load_graph(s) {
    s.graph.nodes().forEach(function(node) {
        node.type = 'border';
    });
    s.graph.edges().forEach(function(edge) {
      edge.hidden = true;
    });
    implement_clickfunction(s);
}

/**
* GRAPH CUTTING ON SIZE OF NODES
*/
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
		// TODO: validate that the requested method is supported. list.indexOf( method )
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


function print_clusters() {
    var checkedBoxes = document.querySelectorAll('input[name=Checkboxclusters]:checked');
    var list_of_clusters = []
    for (var item of checkedBoxes) {
     list_of_clusters.push(item.value)
    }
    s.graph.nodes().forEach(function(node) {
      node.hidden = !(list_of_clusters.includes(JSON.stringify(node.attributes.modularity_class)));
    });
    s.refresh();
}


