/* Author: Zhanhua Hu
 * Created for SCCR, 2018
 */

/**
 * Helper function to determine which calendar should be displayed on the
 * '/calendars' page
 * @param {string} calendarType - The type of calendar that the user requests
 * @param {string} isMobile - The boolean value passed to the function signature
 *                            which indicates if the user agent is a phone or
 *                            not.
 */
function whichCalendar(calendarType, isMobile)
{
    if (isMobile == "True")
    {
        // The case where the calendar requested is "food"
        if (calendarType == "food")
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?showNav=0&amp;showDate=0&amp;showPrint=0&amp;showTabs=0&amp;showCalendars=0&amp;showTz=0&amp;height=400&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=hv4cl31tra0t7l0ggbfrev6tes%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"300\" height=\"400\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
        // The case where the calendar requested is "drugs"
        else if (calendarType == "drugs")
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?showNav=0&amp;showDate=0&amp;showPrint=0&amp;showTabs=0&amp;showCalendars=0&amp;showTz=0&amp;height=400&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=nu02uodssn6j0ij4o3l4rqv9dk%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"300\" height=\"400\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
        // The case where the calendar requested is "health"
        else if (calendarType == "health")
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?showNav=0&amp;showDate=0&amp;showPrint=0&amp;showTabs=0&amp;showCalendars=0&amp;showTz=0&amp;height=400&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=vlqtpo7ig0mbvpmk91j8r736kk%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"300\" height=\"400\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
        // The case where the calendar requested is "shower"
        else
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?showNav=0&amp;showDate=0&amp;showPrint=0&amp;showTabs=0&amp;showCalendars=0&amp;showTz=0&amp;height=400&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=uk8elskt37v991sbe3k7qasu1k%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"300\" height=\"400\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
    }
    else
    {
        // The case where the calendar requested is "food"
        if (calendarType == "food")
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=hv4cl31tra0t7l0ggbfrev6tes%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
        // The case where the calendar requested is "drugs"
        else if (calendarType == "drugs")
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=nu02uodssn6j0ij4o3l4rqv9dk%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
        // The case where the calendar requested is "health"
        else if (calendarType == "health")
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=vlqtpo7ig0mbvpmk91j8r736kk%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
        // The case where the calendar requested is "shower"
        else
        {
            $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=uk8elskt37v991sbe3k7qasu1k%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
        }
    }
}


/**
 * Helper function to determine the appropriate location of the user to be displayed.
 * See https://stackoverflow.com/a/34339799
 * Specifically geared to be used on the '/details' endpoint
 * @param {string} userAddress - The address to be queried, generally the location
 * parameter passed
 * @param {boolean} origin - As passed by the Python caller, if there is an
 * origin, then simply pass it along to this helper method. If not, then
 * we will be injecting the other iframe string into the div element and the
 * boolean value 'false' will be passed through the function body.
 * @returns {null}
 */
function doGeocode(userAddress, origin)
{
    // String that will be appended into the "#gmaps" div
    var htmlString = "";
    // Get geocoder instance
    var geocoder = new google.maps.Geocoder();
    // Geocode the address
    geocoder.geocode({
        'address': userAddress
    }, function(results, status) {
        if (status === google.maps.GeocoderStatus.OK && results.length > 0)
        {
            // Set it to the correct, formatted address if it's valid
            userAddress = results[0].formatted_address;
            // Constant static HTML to be appended to the end of the query string
            const restOfHTML = "<br /><br /><button type=\"button\" class=\"btn btn-primary\">" +
                               "export to ical</button><button type=\"button\" class=\"btn btn-primary\">" +
                               "export to google calendars</button>";
            // Comparison to see if the address has an ampersand character. The
            // Gmaps API will deem this character invalid in the query string.
            // In the case we find such a character, simply replace it with
            // the actual word.
            if (userAddress.indexOf('&') > -1)
            {
                userAddress = userAddress.replace('&', "and")
            }
            // Comparison to see which string we will be injecting into the div
            if (origin)
            {
                var queryStr = "<iframe width=\"300\" height=\"300\" frameborder=\"0\" style=\"border:0\"" +
                                "src=\"https://www.google.com/maps/embed/v1/directions?key=AIzaSyDY3_muYN8O" +
                                "6uGzGGRE35Xj_OPAMVrup4g&origin=" + origin + "&destination=" + userAddress
                                + "\" allowfullscreen></iframe>" + restOfHTML;
                $("#gmaps").empty().append(queryStr);
            }
            else
            {
                var queryStr = "<iframe width=\"300\" height=\"300\" frameborder=\"0\" style=\"border:0\"" +
                               "src=\"https://www.google.com/maps/embed/v1/directions?key=AIzaSyDY3_muYN8O" +
                               "6uGzGGRE35Xj_OPAMVrup4g&q=" + userAddress + "\" allowfullscreen></iframe>" +
                               restOfHTML;
                $("#gmaps").empty().append(queryStr);
            }
        // If this is not the case, then we will inject a "sorry" message
        // into the HTML div element
        }
        else
        {
            $("#gmaps").empty().append("<h1>Sorry, no maps available!</h1>");
        }
    });
};
