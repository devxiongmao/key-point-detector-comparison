function ValidateInput(){
	var operationSelect = 0;
	if ((document.getElementById("matching-select").checked) || (document.getElementById("stitching-select").checked)){
		operationSelect = 1;
	} else{
		operationSelect = 0;
	}

	var ready = 0;
	var checkboxes = document.getElementsByTagName('input');
	for (var i = 0; i < checkboxes.length; i++) {
	    if (checkboxes[i].type === 'checkbox' && checkboxes[i].checked) {
	        ready = 1;
	        break;    
	    }
	}

	var descriptorSelected = 0;
	if (document.getElementById('descriptor-sift').checked){
		descriptorSelected = 1;
	}

	var fileSelected = 0;
	if(document.getElementById("image-l").value != "") {
	   if(document.getElementById("image-r").value != "") {
		   fileSelected = 1;
		}
	}

	var orientationSelect = 0;
	if(document.getElementById("sift-orientation").checked || document.getElementById("downward-orientation").checked) {
	   orientationSelect = 1;
	}
	
	var numOfKeypointsCorrect = 0;
	var keypointsSpecified = document.getElementById("num-keypoints").value;
	var patt = new RegExp("\\D");
	var res = patt.test(keypointsSpecified);
	console.log(res);
	var integer = parseInt(keypointsSpecified, 10);
	if((integer >= 500) && !res){
	   numOfKeypointsCorrect = 1;
	}

	if((orientationSelect == 1) && (descriptorSelected == 1) && (ready == 1) && (operationSelect == 1) && (fileSelected == 1) && (numOfKeypointsCorrect == 1)){
		document.getElementById("submit").disabled = false;
	}else{
		document.getElementById("submit").disabled = true;
	}
}