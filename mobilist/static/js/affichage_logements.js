// Creation d'un object personalisé via un consructeur car je ne peux pas le faire en TS
function Logement(logement_element_id, id_logement, nom_logement){
    this.logement_element_id=logement_element_id;
    this.id_logement=id_logement;
    this.nom_logement=nom_logement;
    this.toString=function() { 
        console.log(this.id_logement, this.nom_logement);
    };
}    

// declaration des variables
const array_logement_obj = Array();
const array_logement = Array();
let selected_logement_elementID = String();
let select_logement_dbID = Number();

// Ecouteur d'événement pour le click sur un logement
document.addEventListener("DOMContentLoaded", function(){
    console.log("DOM chargé");
    array_logement.forEach(element => {
        element.addEventListener("click", function(){
            // element.style.backgroundColor = "red";
            selected_logement_id = element.id;
            select_logement_dbID = parseInt(array_logement_obj.find(logement => 
                logement.logement_element_id === selected_logement_id).id_logement
            );
            console.log("logement cliqué",selected_logement_id);
            console.log("selected element_id type",typeof(selected_logement_id));
            console.log("selected logement dbID",select_logement_dbID);
            console.log("selected element_db_id type",typeof(select_logement_dbID));
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
