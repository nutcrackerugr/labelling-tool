var baseurl = window.location.pathname.replace("batchupload", "");

if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/", last_time = new Date();

function setAuth(xhr)
{
	if (Math.floor((new Date() - last_time) / 60000) >= 5)
	{
		$.ajax({
			async: false,
			type: "GET",
			url: api + "auth/token/valid",
			error: function(xhr)
			{
				if (xhr.status == 403)
				{
					$.ajax({
						async: false,
						type: "POST",
						url: api + "auth/token/refresh",
						headers: {
							"X-CSRF-TOKEN": Cookies.get("csrf_refresh_token")
						},
						success: function()
						{
							last_time = new Date();
						},
						error: function()
						{
							alert("Your session has expired. Please log in again");
							window.location.replace(baseurl);
						}
					});
				}
			}
		});
	}

	return true;
}

function create_error(msg)
{
	if ($("#errormessage").length == 0)
		$("#errorcol").prepend('<div class="alert alert-danger mt-4" id="errormessage"><i class="fa fa-exclamation-triangle" aria-hidden="true"></i> Something went wrong :(<br />' + msg + '</div>');
	else
		$("#errormessage").html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> Something went wrong :(<br />' + msg + '</div>')
}

function clear_error()
{
	if ($("#errormessage").length != 0)
		$("#errormessage").remove();
}

function uploadbatch(event)
{
	var elem = $("#uploadbutton");
	elem.prop("disable", true).html('<i class="fa fa-spinner fa-spin" aria-hidden="true"></i>');

	try
	{
		var payload = JSON.parse($("#batch").val());
		
		$.ajax({
			beforeSend: setAuth,
			type: "POST",
			url: api + "tweet/create/batch",
			headers: {
				"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
			},
			data: JSON.stringify(payload),
			contentType:"application/json",
			dataType: "json",
			success: function(data)
			{
				clear_error();
				$("#batch").val("");
				elem.prop("disable", false).html('<i class="fa fa-check" aria-hidden="true"></i>');
				setTimeout(function()
				{
					elem.html("Upload Batch");
				}, 2000);
			},
			error: function(data)
			{
				create_error(data.responseJSON["message"] || data.responseJSON["msg"]);
				elem.prop("disable", false).html("Upload Batch");
			}
		});
	}
	catch (error)
	{
		create_error("There was a problem when parsing your JSON. Please, check it and try again.");
		elem.prop("disable", false).html("Upload Batch");
	}
	
	event.preventDefault();
	return false;
}

$(function()
{
	$("#uploadbutton").click(uploadbatch);
	$("#batchform").submit(uploadbatch);
});
