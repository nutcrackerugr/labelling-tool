var lastIndexBaseUrl = window.location.pathname.indexOf("stats");
var baseurl = window.location.pathname.substring(0, lastIndexBaseUrl);
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var last_time = 0;

function stopPropagation(e)
{
	e.stopImmediatePropagation();
}

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
				if (xhr.status == 403 || xhr.status == 401)
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
							console.info("Token renewed")
						},
						error: function()
						{
							alert("Your session has expired. Please log in again");
							window.location.replace(baseurl);
						}
					});
				}
			},
			success: function()
			{
				last_time = new Date();
			}
		});
	}

	return true;
}

function createResults(data)
{
	if ($.isEmptyObject(data))
		alert("There are not any results")
	else
	{
        $.each(data, function(k, userdata)
        {
            $("#cards").append('<div class="card p-3 rounded tweetcard"> \
            <div class="card-body"> \
            <h5 class="mt-0 card-title"><i class="fa fa-user" aria-hidden="true"></i> ' + userdata["name"] + ' <span class="text-secondary">(' + userdata["username"] + ')</span></h5> \
            <ul> \
                <li>Annotations: ' + userdata["annotations"] + '</li> \
                <li>Reviewed user annotations: ' + userdata["reviewed_annotations"] + '</li> \
            </ul> \
            </div></div>');
        });
    }
}

$(function()
{
    //Renew tokens if necessary
    setAuth();
    $("#logo").addClass("fa-spin");

    $.ajax({
        beforeSend: setAuth,
        url: api + "stats",
        success: function(data)
        {
            if ($.isEmptyObject(data))
                alert("There are no stats");
            else
            {
                $("#cards").append('<div class="card p-3 rounded tweetcard"> \
                <div class="card-body"> \
                <h5 class="mt-0 card-title"><i class="fa fa-server" aria-hidden="true"></i> General Stats</h5> \
                <ul> \
                    <li>Tweets: ' + data["no_tweets"] + '</li> \
                    <li>Users: ' + data["no_users"] + '</li> \
                    <li>Annotations: ' + data["no_annotations"] + ' (not unique)</li> \
                    <li>AI User Annotations: ' + data["total_user_annotations"] + ' (not unique)</li> \
                    <li>Unique AI User Annotations: ' + data["no_user_annotations"] + '</li> \
                </ul> \
                </div></div>');


                createResults(data["users"]);
            }
        },
        complete: function()
		{
			$("#logo").removeClass("fa-spin");
		}
    });
});