var LEDarr = {
  "width":"32",
  "height":"8",
  "color":"red",
  "mask":"resources/mask2_tp.png",
  "scale":"50"
};

var states = []; //Stores state of all pixels

var mask = new Image();
mask.src=LEDarr.mask;


var canvas = document.getElementById('pixelarray');
var ctx = canvas.getContext('2d');

function clearDots(){
  canvas.height=LEDarr.height*LEDarr.scale;
  canvas.width=LEDarr.width*LEDarr.scale;

  for(var x=0;x<LEDarr.width;x++){
    for(var y=0;y<LEDarr.height;y++){
      ctx.fillStyle = "grey";
      ctx.fillRect(x*LEDarr.scale,y*LEDarr.scale,LEDarr.scale,LEDarr.scale);
      ctx.drawImage(mask,x*LEDarr.scale,y*LEDarr.scale,LEDarr.scale,LEDarr.scale);
    }
  }
}

function renderDots(dotArray){
  for(var i=0;i<dotArray.length;i++){
    if(dotArray[i][2] == undefined){
      ctx.fillStyle = LEDarr.color;
    }else{
      ctx.fillStyle = dotArray[i][2];
    }
    ctx.fillRect(dotArray[i][0]*LEDarr.scale,dotArray[i][1]*LEDarr.scale,LEDarr.scale,LEDarr.scale);
    ctx.drawImage(mask,dotArray[i][0]*LEDarr.scale,dotArray[i][1]*LEDarr.scale,LEDarr.scale,LEDarr.scale);
  }
}

function initStates() {
    for(var y=0;y<LEDarr.height;y++){
      states[y]=[];
      for(var x=0;x<LEDarr.height;x++){
        states[y][x]=undefined;
      }
    }
}

initStates();
resizeView();
//window.addEventListener('resize', resizeView, false);


function resizeView(){
  //LEDarr.scale=Math.floor(((window.innerWidth-500)/LEDarr.width));
  clearDots();
  daDots=[[0,0,"green"],[1,1,"#ABC"],[2,2]];
  renderDots(daDots);
}

function decodeRes(){

}
