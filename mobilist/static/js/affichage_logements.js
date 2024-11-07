// Creation d'un object personalisé via un consructeur JS ne support pas les interfaces (TS oui)
function Logement(logement_element_id, id_logement, nom_logement, type_logement, 
    adresse_logement, description_logement) {
        this.logement_element_id=logement_element_id;
        this.id_logement=id_logement;
        this.nom_logement=nom_logement;
        this.type_logement=type_logement;
        this.adresse_logement=adresse_logement;
        this.description_logement=description_logement;
        this.toString=function() { 
            console.log(this.id_logement, this.nom_logement);
        };
    }    

// declaration des variables
const array_logement_obj = Array();
const array_logement = Array();
let selected_logement_elementID = String();
let selected_logement_dbID

// Attribution des EventListener apres le DOM est chargé
document.addEventListener("DOMContentLoaded", function(){
    console.log("DOM chargé");
    array_logement.forEach(element => {
        element.addEventListener("click", function(){
            // element.style.backgroundColor = "red";
            selected_logement_id = element.id;  
            selected_logement_dbID = parseInt(array_logement_obj.find(logement => 
                logement.logement_element_id === selected_logement_id).id_logement
            );
            console.log("logement cliqué",selected_logement_id);
            console.log("selected element_id type",typeof(selected_logement_id));
            console.log("selected logement dbID",selected_logement_dbID);
            console.log("selected element_db_id type",typeof(selected_logement_dbID));
            updateAllElementStyle();
            console.log("selected logement clicked, change style");
        });
    });

    // Test de la fonction forEach
    console.log("array logement forEach");
    array_logement.forEach(element => {
       console.log(element);
    });

});

// Fonction pour ajouter un logement à un tableau
function addLogementToArray(array,element) {
    array.push(element);
    console.log("current array:",array);
}

// Fonction pour mettre à jour le style de tous les éléments
function updateAllElementStyle() {
    array_logement.forEach(element => {
        element.style.border = "2px dotted black";
        if (element.id === selected_logement_id) {
            element.style.border = "2px solid green";
        }
    });
}

// Fonction pour afficher un form cacher de part son id 
function toggleFormPopup(overlay_id) {
    console.log("overlay_id form", overlay_id);
    if (selected_logement_dbID !== undefined) {
        const overlay = document.getElementById(overlay_id);
        if (overlay_id === 'edit-popup-form') {
            preFillEditForm();
        }else if (overlay_id === 'delete-popup-form') {
            preFillDeleteForm();
        }
        overlay.classList.toggle('show');
        for (i = 0; i < document.getElementsByClassName('action-btn').length; i++) {
            if (document.getElementsByClassName('action-btn')[i].style.display === 'none') {
                document.getElementsByClassName('action-btn')[i].style.display = 'block';
            } else {
                document.getElementsByClassName('action-btn')[i].style.display = 'none';
            }
        }
    } else {
        console.log("logement non sélectionné");
        // window.alert("Veuillez sélectionner un logement");
        messagePopup('unselected-logement-popup');
    }
}

// Fonction pour afficher un message popup
function messagePopup(overlay_id) {
    const overlay = document.getElementById(overlay_id);
    overlay.classList.toggle('show');
}

// Fonction pour pré-remplir le formulaire d'édition
function preFillEditForm() {
    console.log("selected logement dbID",selected_logement_dbID);
    const logement = array_logement_obj.find(logement => logement.id_logement === String(selected_logement_dbID));
    console.log("logement trouvé",logement);
    document.getElementById('edit-id-input').value = logement.id_logement;
    document.getElementById('edit-name-input').value = logement.nom_logement;
    document.getElementById('edit-type-input').value = logement.type_logement;
    document.getElementById('edit-adress-input').value = logement.adresse_logement;
    document.getElementById('edit-description-input').value = logement.description_logement;
}

// Fonction pour préremplir le formulaire de suppression
function preFillDeleteForm() {
    console.log("selected logement dbID",selected_logement_dbID);
    const logement = array_logement_obj.find(logement => logement.id_logement === String(selected_logement_dbID));
    console.log("logement trouvé",logement);
    document.getElementById('delete-id-input').value = logement.id_logement;
    document.getElementById('delete-name-input').value = logement.nom_logement;
}