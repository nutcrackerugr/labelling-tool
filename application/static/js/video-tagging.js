var lastIndexBaseUrl = Math.max(window.location.pathname.indexOf("annotate"), window.location.pathname.indexOf("review"));
var baseurl = window.location.pathname.substring(0, lastIndexBaseUrl);
if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

var video = null, timer = null, openSegments = [], segments = [], labels = [], last_time = 0;

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

function secondsToTime(secs)
{
    return new Date(secs * 1000).toISOString().substr(11, 8);
}

function timeToSeconds(timestamp)
{
    return timestamp.split(':').reduce((acc,time) => (60 * acc) + +time);
}

function updateCurrentTime(e)
{
    timer.val(secondsToTime(video.currentTime));
}

function moveVideoToTime(e)
{
    video.currentTime = timeToSeconds(timer.val());
}

function toggleButton(e)
{
    $(e.target).toggleClass("btn-primary btn-secondary");
}

function removeSegment(element)
{
    if (confirm("Are you sure you want to delete this segment?"))
    {
        $.ajax({
            beforeSend: setAuth,
            type: "DELETE",
            url: api + "video/" + videoname + "/annotation/" + element.data("id") + "/",
            statusCode: {
                403: function(xhr)
                {
                    alert("Your session has expired. Please log in again");
                    window.location.replace(baseurl);
                }
            },
            headers: {
                "X-CSRF-TOKEN": Cookies.get("csrf_access_token")
            },
            contentType: "application/json",
            dataType: "json",
            success: () => element.remove()
        });
    }
}

function saveVideoAnnotation(startTime, endTime, labels, callback)
{
    let payload = {
        "start_time": startTime,
        "end_time": endTime,
        "labels": labels,
        "video": videoname,
    }

    $.ajax({
		beforeSend: setAuth,
		type: "POST",
		url: api + "video/" + videoname + "/annotation/",
		statusCode: {
			403: function(xhr)
			{
				alert("Your session has expired. Please log in again");
				window.location.replace(baseurl);
			}
		},
		headers: {
			"X-CSRF-TOKEN": Cookies.get("csrf_access_token")
		},
		data: JSON.stringify(payload),
		contentType: "application/json",
		dataType: "json",
		success: callback
	});
}

function createSegmentComponent(id, startTime, endTime, selected)
{
    let html = '<div class="d-flex align-items-center segment mb-1">\
        <div class="d-flex flex-column">\
            <span><i class="fa fa-clock-o" aria-hidden="true"></i> ' + secondsToTime(startTime) + ' - ' + secondsToTime(endTime) + '</span>\
            <div class="labels d-flex flex-column"></div>\
        </div>\
        <div class="btn-group ml-auto controls"></div>\
    </div>';

    let element = $(html).data("id", id);

    Object.keys(selected).forEach((k) => {
        $(".labels", element).append(
            $("<span class=" + k + ">" + k + ": " + selected[k] + "</span>")
        );
    });
            
    $(".controls", element).append(
        $('<button type="button" class="btn btn-sm btn-primary">Go Start</button>').click(() => video.currentTime = startTime),
        $('<button type="button" class="btn btn-sm btn-primary">Go End</button>').click(() => video.currentTime = endTime),
        $('<button type="button" class="btn btn-sm btn-danger"><i class="fa fa-trash-o" aria-hidden="true"></i></button>').click(() => removeSegment(element))
    );

    $("#segments").prepend(element);

    return element;
}

function createSegment(startTime, endTime, selected)
{
    saveVideoAnnotation(startTime, endTime, selected, function(data) {
        createSegmentComponent(data["id"], data["start_time"], data["end_time"], data["labels"]);
    });
}

function endOpenSegment(element)
{
    let currentSegment = element;
    let startTime = currentSegment.data("startTime");
    let endTime = video.currentTime;

    let selected = {}

    labels.forEach((l) => {
        selected[l["name"]] = $.map(
            $("." + l["name"] + "-container > button.btn-primary", currentSegment),
            (e) => $(e).html()
        );
    });

    createSegment(startTime, endTime, selected);
    element.remove();
}

function removeOpenSegment(element)
{
    if (confirm("Are you sure you want to delete this unfinished segment?"))
        element.remove();
}

function createOpenSegmentComponent(startTime)
{
    let html = '<div class="open-segment mb-1">\
                    <div class="d-flex justify-content-between align-items-center">\
                        <span class="segment-start"><i class="fa fa-clock-o" aria-hidden="true"></i> ' + secondsToTime(startTime) + '</span>\
                        <div class="btn-group segment-controls" role="group" aria-label="Open Segment Control">\
                        </div>\
                    </div>\
                    <form class="d-flex flex-column align-items-start form-inline mt-2 control-container"></form>\
                </div>';
    
    let element = $(html);
    element.data("startTime", startTime);
    $("#open-segments").append(element);

    $(".segment-controls", element).append(
        $('<button type="button" class="btn btn-sm btn-success end-open-segment">End here</button>').click(() => endOpenSegment(element)),
        $('<button type="button" class="btn btn-sm btn-danger remove-open-segment"><i class="fa fa-trash-o" aria-hidden="true"></i></button>').click(() => removeOpenSegment(element))
    );

    labels.forEach(e => {
        let btn_group = $('<div class="mb-1 btn-group btn-group-sm ' + e["name"] + '-container" role="group" aria-label="' + e["name"] + ' Control"></div>').append(
            $('<button type="button" class="btn btn-secondary" disabled>' + e["name"] + '</button>'));
            
            e["values"].split(",").forEach(v => {
                btn_group.append(
                    $('<button type="button" class="btn btn-secondary" class="' + e + '-' + v + '">' + v + '</button>').click(toggleButton)
                    );
            });
            
            $(".control-container", element).append(btn_group);
        });
}

$(function()
{
    video = document.getElementById("currentVideo");
    timer = $("#currentTime");

    $(video).on("timeupdate", updateCurrentTime);
    timer.on("change", moveVideoToTime);

    $("#addSegment").click(() => createOpenSegmentComponent(video.currentTime));

    //Get labels and insert them in DOM
	$.ajax({
		beforeSend: setAuth,
		url: api + "video/labels",
		success: (data) => labels = data,
	});


    $.ajax({
        beforeSend: setAuth,
        url: api + "video/" + videoname + "/annotations",
        success: (data) => {
            data.forEach((e) => createSegmentComponent(e["id"], e["start_time"], e["end_time"], e["labels"]));
        }
    });
    
});