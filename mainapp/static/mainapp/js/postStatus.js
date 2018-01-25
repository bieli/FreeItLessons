(function ( $ ) {
	$.fn.postStatus = function( options ) {
		  
		// Get options
		var settings = $.extend({
			// These are the defaults for our options
			url: "",
			title: "",
			description: "",
			image: "",
			sites: "",
			orientation: "vertical", // horizontal or vertical button orientation
			shareType: "text", // button (shows a togglable share button), none (shows nothing), text (shows Share on: text before buttons)
			triggerButtonActiveState: false, // Only works with shareType of button... determines if the button should be clicked when created
			buttonSide: "left", // Only works with shareType of button... places the button on the left or right side of the social media icons
			facebookAppId: "", // A facebook developer app id... gives you more control over what you can customize when sharing on FB
		}, options );
		
		// Supported buttons
		var supportedStatuses = new Array('hidden', 'visible', 'in_progress', 'question', 'done');
		var socialMediaButtonsToRun = new Array();
		
		// Variables
		var html = "";
		var additionalStylingForSitesCon = "";
		var attr = null;
		
		// Detect Mobile:
		var isMobile = false;
		if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
			|| /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) isMobile = true;
		
		// Settings processing
		configEmptySettingsDefaultsBasedOnPage();
		
		return this.each(function() {	
			// Unbind previously bound events if any...	
			// Just in case this happens again, which it shouldn't.
			$(this).off();
							
			// Start html building
			html = "<div class='postStatusMainBlockContainer'><div class='postStatusTable'>";
			
			// Reverse the HTML building order if shareType is button and buttonSide is right
			if(settings.buttonSide == "right" && settings.shareType == "button"){
				// Build the HTML responsible for the social network icons which user will click on to share based on settings passed
				html += buildSocialMediaButtonHTML($(this));
				
				// Handle the share button, share text, or not displaying this portion at all
				html += buildShareButtonTextNoneHTML($(this));
			}else{
				// Handle the share button, share text, or not displaying this portion at all
				html += buildShareButtonTextNoneHTML($(this));
				
				// Build the HTML responsible for the social network icons which user will click on to share based on settings passed
				html += buildSocialMediaButtonHTML($(this));
			}	
			
			html += "</div></div>";
			
			// Set the HTML in the container
			$(this).html(html);			
			
			// Handle additional styles
			if(additionalStylingForSitesCon != ""){
				$("div.postStatusSitesContainer", $(this)).attr('style', additionalStylingForSitesCon);
			}
			
			// Set inline style for orientation
			if(settings.orientation == "vertical"){
				$("div.postStatusSitesContainer").css('width', '50px');
			}else if(settings.orientation == "horizontal"){
				$("div.postStatusSitesContainer").css('width', '');
			}
		});
		
		function openWindow(url){
			var width = 640;
			var height = 480;
			var left = (screen.width/2)-(width/2);
			var top = (screen.height/2)-(height/2);
			window.open(url, "_blank", "height=" + height + ",width=" + width + ",location=1,status=1,scrollbars=1,top=" + top + ",left=" + left);
		}
		
		function buildShareButtonTextNoneHTML(instance){
			var html = "";
			
			// Share text, button, or nothing
			if(settings.shareType == "text" && settings.orientation != "vertical"){
				html += "<div class='postStatusTableCell'><div class='postStatusText'>Share on:</div></div>";
			}else if(settings.shareType == "button"){
				html += "<div class='postStatusTableCell'><div class='postStatusButton";
				if(settings.buttonSide == "right"){
					html += "OnRight";
				}
				if(settings.triggerButtonActiveState === true){
					html += " postStatusButtonActive";
				}
				html += "'>SHARE</div></div>";
				
				// Bind onclick for button 
				$(instance).on('click', 'div.postStatusButton, div.postStatusButtonOnRight', function() {			
					if(!$("div.postStatusSitesContainer", $(instance)).is(":visible")){				
						$("div.postStatusSitesContainer", $(instance)).css('display', 'inline-block');
						$(this).removeClass('postStatusButtonActive').addClass('postStatusButtonActive');
					}else{
						$("div.postStatusSitesContainer", $(instance)).css('display', 'none');
						$(this).removeClass('postStatusButtonActive');
					}
				});
				
				if(settings.triggerButtonActiveState == false){
					additionalStylingForSitesCon = "display: none;";
				}
			}
			
			return html;
		}
		
		function buildSocialMediaButtonHTML(instance){
			var html = "";
			var capitalizedSocialNetwork = null;

			// Encode all important parmas we gonna pass in
			var shareTitle = encodeURIComponent(settings.title);
			var shareDesc = encodeURIComponent(settings.description);
			var shareURL = encodeURIComponent(settings.url);
			var shareImage = encodeURIComponent(settings.image);

			// HTML for the various social media sites
			html += "<div class='postStatusSitesContainer postStatusTableCell clearfix'><ul>"; 
			if(socialMediaButtonsToRun.length > 0){
				for(var i = 0; i < socialMediaButtonsToRun.length; i++){
					capitalizedSocialNetwork = socialMediaButtonsToRun[i].charAt(0).toUpperCase() + socialMediaButtonsToRun[i].slice(1);
					
					if(socialMediaButtonsToRun[i] != "whatsapp"){
						html += '<li class="postStatus' + capitalizedSocialNetwork + ' postStatusSiteContainer" title="Share via ' + capitalizedSocialNetwork + '"></li>';
					}else{
						// Only show Whatsapp if mobile
						if(isMobile){
							html += '<li class="postStatus' + capitalizedSocialNetwork + ' postStatusSiteContainer" title="Share via ' + capitalizedSocialNetwork + '"></li>';
						}
					}
					switch(socialMediaButtonsToRun[i]){
						case "hidden":
							loadFacebookSDKIfNeeded();
							$(instance).on('click', 'li.postStatus' + capitalizedSocialNetwork, function() {							
								if(window.FB && settings.facebookAppId != ""){
									// Use non-encodeURIComponent URLS for FB
									FB.ui({
										method: 'feed',
										name: settings.title,
										link: settings.url,
										picture: settings.image,
										description: settings.description,
									});
								}else{
									openWindow("https://www.facebook.com/sharer/sharer.php?u=" + shareURL);
								}
							});
							break;
						case "visible":
							$(instance).on('click', 'li.postStatus' + capitalizedSocialNetwork, function() {							
								openWindow("https://twitter.com/intent/tweet?text=" + shareDesc + "&url=" + shareURL);
							});
							break;
						case "in_progress":
							$(instance).on('click', 'li.postStatus' + capitalizedSocialNetwork, function() {							
								openWindow("https://plus.google.com/share?url=" + shareURL);
							});
							break;
						case "question":
							$(instance).on('click', 'li.postStatus' + capitalizedSocialNetwork, function() {							
								openWindow("https://www.linkedin.com/shareArticle?url=" + shareURL + "&mini=true&title=" + shareTitle + "&summary=" + shareDesc);
							});
							break;
						case "done":
							$(instance).on('click', 'li.postStatus' + capitalizedSocialNetwork, function() {							
								openWindow("http://www.reddit.com/submit?url=" + shareURL + "&title=" + shareTitle);
							});
							break;
					}
				}
			}
			html += "</ul></div>";

			return html;
		}
		
		function loadFacebookSDKIfNeeded(){
			if (!window.FB && settings.facebookAppId != ""){
				$.getScript('https://connect.facebook.net/en_US/sdk.js', function(){
					FB.init({
						appId: settings.facebookAppId,
						version: 'v2.5' // or v2.0, v2.1, v2.2, v2.3
					});  
				});
			}
		}
		
		function configEmptySettingsDefaultsBasedOnPage(){
			if(settings.url == ""){
				settings.url = window.location.href;
			}
			
			if(settings.title == ""){
				settings.title = document.getElementsByTagName("title")[0].innerHTML;
			}
			
			// Get which social media sites to run
			if(settings.sites == ""){
				settings.sites == "all";
				socialMediaButtonsToRun = supportedStatuses;
			}else{
				if(settings.sites.indexOf(",") != -1){
					var tmpArray = settings.sites.split(",");
					for(var i = 0; i < tmpArray.length; i++){
						if($.inArray(tmpArray[i].toLowerCase(), supportedStatuses) != -1){
							socialMediaButtonsToRun.push(tmpArray[i].toLowerCase());
						}
					}
				}else{
					if($.inArray(settings.sites.toLowerCase(), supportedStatuses) != -1){
						socialMediaButtonsToRun.push(settings.sites.toLowerCase());
					}
				}
			}
			
			// If we didn't get any valid options
			// Default to loading all
			if(socialMediaButtonsToRun.length == 0){
				socialMediaButtonsToRun = supportedStatuses;
			}
			
			if(settings.description == ""){
				var descMeta = $('meta').filter(function() {
					if(typeof $(this).attr('name') !== typeof undefined && $(this).attr('name') !== false){
						return $(this).attr('name').toLowerCase().indexOf('description') > -1;
					}else{
						return false;
					}
				});
				if(descMeta.length){
					attr = descMeta.first().attr('content');
					if (typeof attr !== typeof undefined && attr !== false) {
						settings.description = attr;
					}
				}
			}
			
			if(settings.image == ""){
				// Load default if it exists
				// OG IMAGE IS FIRST
				var metaOGImage = $('meta').filter(function() {
					if(typeof $(this).attr('property') !== typeof undefined && $(this).attr('property') !== false){
						return $(this).attr('property').toLowerCase().indexOf('og:image') > -1;
					}else{
						return false;
					}
				});
				if(metaOGImage.length){
					attr = metaOGImage.first().attr('content');
					if (typeof attr !== typeof undefined && attr !== false) {
						settings.image = attr;
					}
				}
				
				// If it's still empty, try twitter
				if(settings.image == ""){
					var twitImage = $('meta').filter(function() {
						if(typeof $(this).attr('property') !== typeof undefined && $(this).attr('property') !== false){
							return $(this).attr('property').toLowerCase().indexOf('twitter:image') > -1;
						}else{
							return false;
						}
					});
					if(twitImage.length){
						attr = twitImage.first().attr('content');
						if (typeof attr !== typeof undefined && attr !== false) {
							settings.image = attr;
						}
					}
				}
			}
		}
	
	};
}( jQuery ));
