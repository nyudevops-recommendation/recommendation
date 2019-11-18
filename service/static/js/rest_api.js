$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#recommendation_id").val(res.id);
        $("#product_id").val(res.product_id);
        $("#customer_id").val(res.customer_id);
		$("#recommend_product_id").val(res.recommend_product_id);
        if (res.recommend_type == "upsell") {
            $("#recommend_type").val("upsell");
        } else if (res.recommend_type == "crosssell") {
            $("#recommend_type").val("crosssell");
        } else {
			$("#recommend_type").val("accessory");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#customer_id").val("");
        $("#recommend_product_id").val("");
		$("#recommend_type").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        var proid = $("#product_id").val();
        var cid = $("#customer_id").val();
		var rpid = $("#recommend_product_id").val();
        var type = $("#recommend_type").val();

        var data = {
			"product_id": proid,
            "customer_id": cid,
            "recommend_type": type,
            "recommend_product_id": rpid
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Recommendation
    // ****************************************

    $("#update-btn").click(function () {

        var rid = $("#recommendation_id").val();
        var proid = $("#product_id").val();
        var cid = $("#customer_id").val();
		var rpid = $("#recommend_product_id").val();
        var type = $("#recommend_type").val();

        var data = {
			"product_id": proid,
            "customer_id": cid,
            "recommend_type": type,
            "recommend_product_id": rpid
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/recommendations/" + rid,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });
	
	// ****************************************
    // INCREMENT SUCCESS
    // ****************************************

    $("#success-btn").click(function () {

        var rid = $("#recommendation_id").val();
        

        var ajax = $.ajax({
                type: "PUT",
                url: "/recommendations/" + rid + "/success",
                contentType: "application/json"
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        var rid = $("#recommendation_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations/" + rid,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        var rid = $("#recommendation_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/recommendations/" + rid,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#recommendation_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        var proid = $("#product_id").val();
        var cid = $("#customer_id").val();
		var rpid = $("#recommend_product_id").val();
        var type = $("#recommend_type").val();

        var queryString = ""

        if (proid) {
            queryString += 'product-id=' + proid
        }
        if (cid) {
            if (queryString.length > 0) {
                queryString += '&customer-id=' + cid
            } else {
                queryString += 'customer-id=' + cid
            }
        }
        if (type) {
            if (queryString.length > 0) {
                queryString += '&recommend-type=' + type
            } else {
                queryString += 'recommend-type=' + type
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:10%">Product ID</th>'
            header += '<th style="width:10%">Customer ID</th>'
            header += '<th style="width:10%">Rec Product ID</th></th>'
			header += '<th style="width:10%">Type</th></th>'
			header += '<th style="width:10%">Success</th></tr>'
            $("#search_results").append(header);
            var firstRecommendation = "";
            for(var i = 0; i < res.length; i++) {
                var recommendation = res[i];
                var row = "<tr><td>"+recommendation.id+"</td><td>"+recommendation.product_id+"</td><td>"+recommendation.customer_id+"</td><td>"+recommendation.recommend_product_id+"</td><td>"+recommendation.recommend_type+"</td><td>"+recommendation.rec_success+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstRecommendation = recommendation;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            //if (firstRecommendations != "") {
                update_form_data(firstRecommendation);
            //}

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
