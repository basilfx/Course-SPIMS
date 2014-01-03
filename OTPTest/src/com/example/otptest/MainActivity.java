package com.example.otptest;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import org.apache.http.NameValuePair;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.utils.URLEncodedUtils;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.message.BasicNameValuePair;

import android.app.Activity;
import android.app.AlertDialog;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity implements SensorEventListener {

	private SensorManager sensor = null;
	private long lastSensorUpdate = 0L;

	private float sensorDA2max = 0.0F;
	private float sensorLastAX = 0.0F;
	private float sensorLastAY = 0.0F;
	private float sensorLastAZ = 0.0F;
	
	private float maxAX = 0.0F;
	private float maxAY = 0.0F;
	private float maxAZ = 0.0F;
	
	private float minAX = 0.0F;
	private float minAY = 0.0F;
	private float minAZ = 0.0F;
	
	private long accChange = 0;
	private long startTime = 0;
	private long endTime = 0;
	private long rounds = 0;
	
	private boolean uploading;
	
	private List<Long> valuesAccT;
	private List<Integer> valuesAccX;
	private List<Integer> valuesAccY;
	private List<Integer> valuesAccZ;
	
	private List<Long> valuesGyroT;
	private List<Integer> valuesGyroX;
	private List<Integer> valuesGyroY;
	private List<Integer> valuesGyroZ;
	
	private long count;
	
	private long sessionId = (long) (Math.random() * Long.MAX_VALUE); 
	
	private ProgressBar shakeProgress = null;

	private Button buttonGo;
	private Button buttonRaw;
	private TextView textResult;
	private TextView textCount;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		// Initialize lists
		this.valuesAccT = new ArrayList<Long>(2500);
		this.valuesAccX = new ArrayList<Integer>(2500);
		this.valuesAccY = new ArrayList<Integer>(2500);
		this.valuesAccZ = new ArrayList<Integer>(2500);
		
		this.valuesGyroT = new ArrayList<Long>(1500);
		this.valuesGyroX = new ArrayList<Integer>(1500);
		this.valuesGyroY = new ArrayList<Integer>(1500);
		this.valuesGyroZ = new ArrayList<Integer>(1500);
		
		this.uploading = false;
		
		// Initialize views
		this.shakeProgress = (ProgressBar) this.findViewById(R.id.progressShake);
		this.buttonGo = (Button) this.findViewById(R.id.buttonGo);
		this.buttonRaw = (Button) this.findViewById(R.id.buttonRaw);
		this.textResult = (TextView) this.findViewById(R.id.textResult);
		this.textCount = (TextView) this.findViewById(R.id.textCount);
		
		this.buttonGo.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				enableSensor();
			}
		});
		
		this.buttonRaw.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				if (valuesAccT.size() > 0 || valuesGyroT.size() > 0) {
					MainActivity.this.uploading = true;
					MainActivity.this.buttonRaw.setEnabled(false);
					
					new Thread(new Runnable() {
						@Override
						public void run() {
							// Write file to server
							URL url;
							HttpURLConnection connection;
							DataOutputStream stream;
							
							try {
								url = new URL("http://www.basilfx.net/_upload.php");
								connection = (HttpURLConnection) url.openConnection();
								
								// Enable POST method
								connection.setRequestMethod("POST");
							} catch (IOException e) {
								Log.d(this.getClass().getName(), "Exception", e);
								MainActivity.this.toast("Could not upload result. Make sure your device is connected to the internet.");
								return;
							}
		
							// Allow Inputs & Outputs
							connection.setDoInput(true);
							connection.setDoOutput(true);
							connection.setUseCaches(false);
		
							connection.setRequestProperty("Connection", "Keep-Alive");
							connection.setRequestProperty("Content-Type", "multipart/form-data;boundary=*****");
							
							try {
								stream = new DataOutputStream(connection.getOutputStream());
								stream.writeBytes("--*****\r\n");
								stream.writeBytes("Content-Disposition: form-data; name=\"uploadedfile\";filename=\"result.txt\"" + "\r\n");
								stream.writeBytes("\r\n");
								
								stream.writeBytes("# GeneralV2\n");
								stream.writeBytes(Build.MODEL + "\n");
								stream.writeBytes(sessionId + "\n");
								
								// Write each accelerometer value
								stream.writeBytes("# ACCELEROMETER\n");
								stream.writeBytes(valuesAccT.size() + "\n");
								
								
								for (int i = 0; i < valuesAccT.size(); i++) {
									stream.writeBytes(valuesAccT.get(i) + ";");
									stream.writeBytes(valuesAccX.get(i) + ";");
									stream.writeBytes(valuesAccY.get(i) + ";");
									stream.writeBytes(valuesAccZ.get(i) + "\n");
								}
								
								// Write each gyroscope value
								stream.writeBytes("# GYRO\n");
								stream.writeBytes(valuesGyroT.size() + "\n");
								
								for (int i = 0; i < valuesGyroT.size(); i++) {
									stream.writeBytes(valuesGyroT.get(i) + ";");
									stream.writeBytes(valuesGyroX.get(i) + ";");
									stream.writeBytes(valuesGyroY.get(i) + ";");
									stream.writeBytes(valuesGyroZ.get(i) + "\n");
								}
								
								stream.writeBytes("\r\n");
								stream.writeBytes("--*****\r\n");
								stream.flush();
								stream.close();
								
								// Finalize
								int responseCode = connection.getResponseCode();
								String responseMessage = connection.getResponseMessage();
								
								if (responseCode < 400) {
									throw new IOException("Bad HTTP status");
								}
								
								Log.d(this.getClass().getName(),  "Response code: " + responseCode);
								Log.d(this.getClass().getName(),  "Message: " + responseMessage);
							} catch (IOException e) {
								Log.d(this.getClass().getName(), "Exception", e);
								MainActivity.this.toast("Could not upload result. Make sure your device is connected to the internet.");
								
								return;
							}
							
							final long items = valuesAccT.size() + valuesGyroT.size();
							
							// Clear arrays
							valuesAccT.clear();
							valuesAccX.clear();
							valuesAccY.clear();
							valuesAccZ.clear();
							
							valuesGyroT.clear();
							valuesGyroX.clear();
							valuesGyroY.clear();
							valuesGyroZ.clear();
							
							count = 0;
							
							// Re-enable upload button
							MainActivity.this.runOnUiThread(new Runnable() {
								@Override
								public void run() {
									MainActivity.this.toast("Uploaded " + items + " raw values");
									MainActivity.this.uploading = false;
								}
							});
						}
					}).start();
				}
			}
		});
	}

	@Override
	protected void onPause() {
		this.sensor.unregisterListener(this);
		super.onPause();
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
	    // Handle item selection
	    switch (item.getItemId()) {
	    	case R.id.action_about:
	    		new AlertDialog.Builder(this).setMessage(
	    			"This app evaluates your accelerometer for one-time " +
	    			"password generation for an University of Twente course " +
	    			"on security and privacy. Only sensor data, timestamp " + 
	    			"and model are uploaded."
	    		).setTitle("About").show();
	    		
	    		return true;
	    	default:
	    		return super.onOptionsItemSelected(item);
	    }
	}
	
	private boolean enableSensor() {
		this.sensorLastAX = 0.0F;
		this.sensorLastAY = 0.0F;
		this.sensorLastAZ = 0.0F;
		
		this.maxAX = 0.0F;
		this.maxAY = 0.0F;
		this.maxAZ = 0.0F;
		this.minAX = 0.0F;
		this.minAY = 0.0F;
		this.minAZ = 0.0F;
		
		this.rounds = (long) (Math.random() * 10) + 1;
		this.accChange = 0;
		this.startTime = System.currentTimeMillis();
		this.endTime = 0;
		
		this.lastSensorUpdate = 0L;
		this.sensorDA2max = 0.0F;
		
		this.textResult.setText("Shake until the progress bar is full.");
		this.shakeProgress.setProgress(0);
		this.shakeProgress.setMax((int) rounds);
		
		this.buttonGo.setEnabled(false);
	
		return true;
	}

	@Override
	protected void onResume() {
		super.onResume();
		
		this.sensor = ((SensorManager) this.getSystemService("sensor"));
		Sensor localSensor = this.sensor.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
		Sensor gyroSensor = this.sensor.getDefaultSensor(Sensor.TYPE_GYROSCOPE);

		if (localSensor != null) {
			this.sensor.registerListener(this, localSensor, 3);
		}
		
		if (gyroSensor != null) {
			this.sensor.registerListener(this, gyroSensor, 3);
		}
	}

	public void onSensorChanged(SensorEvent paramSensorEvent) {
		float f1 = paramSensorEvent.values[0];
		float f2 = paramSensorEvent.values[1];
		float f3 = paramSensorEvent.values[2];
		
		if (!this.uploading) {
			if (this.valuesGyroT.size() > 50 || this.valuesAccT.size() > 50) {
				MainActivity.this.buttonRaw.setEnabled(true);
			}
			
			if (paramSensorEvent.sensor.getType() == Sensor.TYPE_GYROSCOPE) {
				this.valuesGyroT.add(paramSensorEvent.timestamp);
				this.valuesGyroX.add(Float.floatToRawIntBits(f1));
				this.valuesGyroY.add(Float.floatToRawIntBits(f2));
				this.valuesGyroZ.add(Float.floatToRawIntBits(f3));
	
				return;
			}
		
			this.valuesAccT.add(paramSensorEvent.timestamp);
			this.valuesAccX.add(Float.floatToRawIntBits(f1));
			this.valuesAccY.add(Float.floatToRawIntBits(f2));
			this.valuesAccZ.add(Float.floatToRawIntBits(f3));
			
			count++;
			
			if (count % 100 == 0) {
				this.textCount.setText(count + "");
			}
		}
		
		if (this.buttonGo.isEnabled() == false) { 
			this.maxAX = Math.max(this.maxAX, f1);
			this.maxAY = Math.max(this.maxAY, f2);
			this.maxAZ = Math.max(this.maxAZ, f3);
			
			this.minAX = Math.min(this.minAX, f1);
			this.minAY = Math.min(this.minAY, f2);
			this.minAZ = Math.min(this.minAZ, f3);
	
			if (this.lastSensorUpdate > 0L) {
				float f4 = f1 - this.sensorLastAX;
				float f5 = f2 - this.sensorLastAY;
				float f6 = f3 - this.sensorLastAZ;
				float f7 = f4 * f4 + f5 * f5 + f6 * f6;
				if (f7 > this.sensorDA2max)
					this.sensorDA2max = f7;
			}
	
			if (this.sensorDA2max > 80.0F) {
				this.shakeProgress.incrementProgressBy(1);
	
				if (this.shakeProgress.getProgress() == this.shakeProgress.getMax()) {
					this.endTime = System.currentTimeMillis();
					
					List<NameValuePair> params = new LinkedList<NameValuePair>();
					params.add(new BasicNameValuePair("model", Build.MODEL));
					params.add(new BasicNameValuePair("endTime", (this.endTime / 1000) + ""));
					params.add(new BasicNameValuePair("startTime", (this.startTime / 1000) + ""));
					params.add(new BasicNameValuePair("sessionId", sessionId + ""));
					params.add(new BasicNameValuePair("sensorDA2max", sensorDA2max + ""));
					params.add(new BasicNameValuePair("rounds", this.rounds + ""));
					params.add(new BasicNameValuePair("maxAX", this.maxAX + ""));
					params.add(new BasicNameValuePair("maxAY", this.maxAY + ""));
					params.add(new BasicNameValuePair("maxAZ", this.maxAZ + ""));
					params.add(new BasicNameValuePair("minAX", this.minAX + ""));
					params.add(new BasicNameValuePair("minAY", this.minAY + ""));
					params.add(new BasicNameValuePair("minAZ", this.minAZ + ""));
					params.add(new BasicNameValuePair("accChange", this.accChange + ""));
					
					final String url = "http://www.basilfx.net/_post.php?" + URLEncodedUtils.format(params, "utf-8");
					
					new Thread(new Runnable() {
						@Override
						public void run() {
							HttpClient client = new DefaultHttpClient();
							
							try {
								client.execute(new HttpGet(url));
							} catch (Exception e) {
								Log.d(this.getClass().getName(), "Exception", e);
								MainActivity.this.toast("Could not upload result. Make sure your device is connected to the internet.");
								
								return;
							}
						}
					}).start();
					
					this.buttonGo.setEnabled(true);
					this.textResult.setText("Result: " + this.sensorDA2max);
				}
	
				this.sensorDA2max = 0.0F;
			}
	
			this.lastSensorUpdate = paramSensorEvent.timestamp;
			this.sensorLastAX = f1;
			this.sensorLastAY = f2;
			this.sensorLastAZ = f3;
		}
	}

	public void toast(final String message) {
		this.runOnUiThread(new Runnable() {
			@Override
			public void run() {
				Toast.makeText(MainActivity.this, message, Toast.LENGTH_LONG).show();
			}
		});
	}
	
	@Override
	public void onAccuracyChanged(Sensor sensor, int accuracy) {
		this.accChange++;
	}
}
