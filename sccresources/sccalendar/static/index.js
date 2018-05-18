/* Author: Zhanhua Hu
 * Created for SCCR, 2018
 */

/**
 * Helper function to determine which calendar should be displayed on the
 * '/calendars' page
 * @param {string} calendarType - The type of calendar that the user requests
 */
function whichCalendar(calendarType)
{
    // The case where the calendar requested is "food"
    if (calendarType == "food")
    {
        $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=hv4cl31tra0t7l0ggbfrev6tes%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
    }
    // The case where the calendar requested is "clothing"
    else if (calendarType == "clothing")
    {
        // TODO
        $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=hv4cl31tra0t7l0ggbfrev6tes%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
    }
    // The case where the calendar requested is "drugs"
    else
    {
        // TODO
        $("#google-cal").empty().append("<iframe src=\"https://calendar.google.com/calendar/embed?mode=WEEK&amp;height=600&amp;wkst=1&amp;bgcolor=%23FFFFFF&amp;src=hv4cl31tra0t7l0ggbfrev6tes%40group.calendar.google.com&amp;color=%230F4B38&amp;ctz=America%2FLos_Angeles\" style=\"border-width:0\" width=\"800\" height=\"600\" frameborder=\"0\" scrolling=\"no\"></iframe>");
    }
}
