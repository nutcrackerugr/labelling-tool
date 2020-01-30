var baseurl = window.location.pathname.replace("signup", "");

if (!baseurl.endsWith('/'))
	baseurl += '/';
	
var api = baseurl + "api/";

function create_error(msg)
{
	if ($("#errormessage").length == 0)
		$("#cardbody").prepend('<div class="alert alert-danger" id="errormessage"><i class="fa fa-exclamation-triangle" aria-hidden="true"></i> Something went wrong :(<br />' + msg + '</div>');
	else
		$("#errormessage").html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> Something went wrong :(<br />' + msg + '</div>')
}

function clear_error()
{
	if ($("#errormessage").length != 0)
		$("#errormessage").remove();
}

function signup(event)
{
	var u = $("#username").val();
	var e = $("#email").val();
	var p = $("#password").val();
	var p2 = $("#password2").val();

	if (p != p2)
		create_error("Passwords do not match.");
	else if (p.length < 6)
		create_error("Password needs to have at least 6 characters.");
	else if (!/[^@]+@[^@]+\.[^@]+/.test(String(e).toLowerCase()))
		create_error("Invalid email address.");
	else
	{
		var payload = {
			"username": u,
			"email": e,
			"password": p,
			"password2": p2
		};
		
		$.ajax({
			type: "POST",
			url: api + "auth/register",
			data: JSON.stringify(payload),
			contentType:"application/json",
			dataType: "json",
			success: function(data)
			{
				clear_error();
				$("#signupform").empty().html("<span>Your user account was created successfully. You need to wait for the site administrator to approve your account before you can log in. In case you need promptness, please, contact the Nutcracker team.</span><br /><a href=\"" + baseurl + "\">Click here to go to the login page</a>.");
			},
			error: function(data)
			{
				create_error(data.responseJSON["message"]);
			}
		});
	}

	event.preventDefault();
	return false;
}

$(function()
{
	$("#signupbutton").click(signup);
	$("#signupform").submit(signup);
});
