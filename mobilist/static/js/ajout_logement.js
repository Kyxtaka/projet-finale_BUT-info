document.addEventListener("DOMContentLoaded", function(){

    
});

function toggleFormPopup(overlay_id) {
    console.log("overlay_id form", overlay_id);
    const overlay = document.getElementById(overlay_id);
    console.log("overlay", overlay);
    overlay.classList.toggle('show');
    for (i = 0; i < document.getElementsByClassName('action-btn').length; i++) {
        document.getElementsByClassName('action-btn')[i].style.display =  document.getElementsByClassName('action-btn')[i].style.display === 'none' ? 'block' : 'none';
    }
    
}