/* Author: Kobe Hu
 * Created for SCCR, 2018
 */

// Self invoking function to begin
$(document).ready(function(){
    // The time each div will fade in or out
    var fadeTime = 1250;
    // Display no divs
    $("div").css("display", "none");
    // Fade into the landing page
    $("#scc-logo").fadeIn(fadeTime);
    // Set a timeout to fade out of the landing page div
    setTimeout(function(){
        $("#scc-logo").fadeOut(fadeTime);
    }, 4000);
    // Fade into the main view
    $("#landing-page").delay(fadeTime * 4.25).fadeIn(fadeTime);
    /* Scroll functions for each of the titles/buttons
     */
    // $("#about-heading").click(function() {
    //     $('html, body').animate({
    //         scrollTop: $("#about-sub").offset().top
    //     }, 1000);
    // });
    // $("#ventures-heading").click(function() {
    //     $('html, body').animate({
    //         scrollTop: $("#ventures-sub").offset().top
    //     }, 1000);
    // });
    // $("#team-heading").click(function() {
    //     $('html, body').animate({
    //         scrollTop: $("#team-sub").offset().top
    //     }, 1000);
    // });
    // $("#contact-heading").click(function() {
    //     $('html, body').animate({
    //         scrollTop: $("#contact-sub").offset().top
    //     }, 1000);
    // });
});
