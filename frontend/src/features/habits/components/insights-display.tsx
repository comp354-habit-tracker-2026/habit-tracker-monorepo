import { useState} from 'react';
import { mockActivities } from '@/app/routes/app/mock-activities';
 export function InsightsDisplay() { 
    const [show, setShow] = useState(false); 

    const activitiesperDay: Record<string, number>={};
    const caloriesperDay: Record<string, number> = {};

    let mostIntenseActivity = mockActivities[0];
    let totalHeartRate = 0;
    let heartrateCount = 0;

    for (const activity of mockActivities) {
        const date = activity.startedAt.slice(0, 10);
        activitiesperDay[date] = (activitiesperDay[date] ||0) +1;
        caloriesperDay[date] = (caloriesperDay[date] ||0) + (activity.summary.calories || 0);

        if (
            (activity.summary.calories || 0) > (mostIntenseActivity.summary.calories || 0)

        ){
         mostIntenseActivity = activity;
        }
        if (activity.summary.avgHeartRate !== undefined) {
            totalHeartRate += activity.summary.avgHeartRate;
            heartrateCount +=1
         }
    }

    let mostActiveDay = '';
    let mostActivites = 0;

    for (const day in activitiesperDay) {
        if (activitiesperDay[day]> mostActivites) {
            mostActivites = activitiesperDay[day];
            mostActiveDay = day;
        }
    }

    let highestCaloryDay = '';
    let highestCalories = 0;

    for (const day in caloriesperDay) {
        if (caloriesperDay[day]> highestCalories) {
            highestCalories = caloriesperDay[day];
            highestCaloryDay = day;
        }
    }

    const averageHeartRate = heartrateCount > 0 ? Math.round(totalHeartRate / heartrateCount) : 0;


    if(!show) { 
        return ( 
        <button onClick={() => setShow(true)}> 
        View your Insights 
        </button> ); 
        } 
        return ( 
        <div>
             <button onClick={() => setShow(false)}> 
                Hide Insights
                 </button> 
                 <div> 
                    <h2>Insights</h2> 
                    <p><strong>Most active day:</strong> {mostActiveDay} ({mostActivites} activities)</p>
                    <p><strong>Highest calories in one day:</strong> {highestCaloryDay} ({highestCalories} calories)</p>
                    <p><strong>Most intense activity:</strong> {mostIntenseActivity.title} ({mostIntenseActivity.activityType}) -{' '}
                     {mostIntenseActivity.summary.calories || 0} calories</p>
                    <p><strong>Average heart rate:</strong> {averageHeartRate} bpm</p>
                    </div>
                 </div> 
                ) 
        }




        /* durationSeconds: 4320,
      distanceKm: 34.8,
      avgSpeedKmh: 29.0,
      maxSpeedKmh: 52.7,
      avgHeartRate: 151,
      avgCadenceRpm: 86,
      avgPowerWatts: 214,
      calories: 740,*/