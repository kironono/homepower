// 端子
const int powLedPin = 13;
const int arefPin = 0;
const int currentPin = 1;

// 電源周波数
#define POWER_FREQ (50)
// 1サイクルあたりのサンプル数
#define NUMBER_OF_SAMPLES (25)
// サンプリング間隔(マイクロ秒)
#define SAMPLING_PERIOD (1000000/(POWER_FREQ * NUMBER_OF_SAMPLES))
// 電圧係数
#define kVT (86.9817579)
// CT係数: R * 系数 / 巻き数
#define kCT (100.0 * 1.00 / 3000.0)
// データ出力の間隔(ミリ秒) (1000 〜)
#define POST_DATA_PERIOD (10000)

// 測定値
float Vrms;
float Irms;
float Watt;

int VASamples[NUMBER_OF_SAMPLES*4];

// 電力を計算
void calcWatt(void) {
  
  unsigned long t1, t2;
  int i, r, v1, v2, a1, a2;
  
  t1 = micros();
  
  for (i = 0; i < NUMBER_OF_SAMPLES; i++) {
    
    r = analogRead(arefPin);
    v1 = 0;
    a1 = analogRead(currentPin);
    a2 = analogRead(currentPin);
    v2 = 0;
  
    VASamples[(i * 4) + 0] = 0;
    VASamples[(i * 4) + 1] = a1 - r;
    VASamples[(i * 4) + 2] = a2 - r;
    VASamples[(i * 4) + 3] = 0;
    
    do {
      t2 = micros();
    } while ((t2 - t1) < SAMPLING_PERIOD);
  
    t1 += SAMPLING_PERIOD;
  }
  
  Vrms = 0;
  Irms = 0;
  Watt = 0;
  
  for (i = 0; i < NUMBER_OF_SAMPLES; i++) {
    v1 = VASamples[(i * 4) + 0];
    a1 = VASamples[(i * 4) + 1];
    a2 = VASamples[(i * 4) + 2];
    v2 = VASamples[(i * 4) + 3];
    
    float vv = ((((v1 + v2) / 2) * 5.0) / 1024) * kVT;
    float aa = ((((a1 + a2) / 2) * 5.0) / 1024) / kCT;
    
    Vrms += vv * vv;
    Irms += aa * aa;
    Watt += vv * aa;
  }
  
  // 2乗平均平方根(rms)を求める
  Vrms = sqrt(Vrms / NUMBER_OF_SAMPLES);
  Irms = sqrt(Irms / NUMBER_OF_SAMPLES);
  
  // 平均電力
  // Watt = Watt / NUMBER_OF_SAMPLES;
  Watt = Irms * 100.0 * 0.9;
  
}

float watt_hour;
float vrms_sum;
float irms_sum;
float watt_sum;
int watt_samples;
unsigned long last_update;
unsigned long last_postdata_time;

void postData(void) {
  Serial.print(irms_sum);
  Serial.print(",");
  Serial.println(watt_sum);
}

void setup() {
  Serial.begin(57600);
  
  digitalWrite(powLedPin, HIGH);
  
  last_update = last_postdata_time = millis();
}

void loop() {
  unsigned long curr_time;
  
  calcWatt();
  
  // 1秒分加算する
  vrms_sum += Vrms;
  irms_sum += Irms;
  watt_sum += Watt;
  watt_samples++;
  
  curr_time = millis();
  if ((curr_time - last_update) > 1000) {
    
    // 1秒分の平均値
    vrms_sum /= watt_samples;
    irms_sum /= watt_samples;
    watt_sum /= watt_samples;
    
    //postData();
    if ((curr_time - last_postdata_time) > POST_DATA_PERIOD) {
      postData();
      
      last_postdata_time = curr_time;
    }
    
    watt_samples = 0;
    vrms_sum = irms_sum = watt_sum = 0;
    
    last_update = curr_time;
  }
}
