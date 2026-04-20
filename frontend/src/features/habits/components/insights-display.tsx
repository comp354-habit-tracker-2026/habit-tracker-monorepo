import { useState} from 'react';
import { mockActivities } from '@/app/routes/app/mock-activities';
 export function InsightsDisplay() { 
    const [show, setShow] = useState(false); 

    const currMonth = new Date();
    const startOfMonth = new Date(currMonth.getFullYear(), currMonth.getMonth(), 1);
    const endOfMonth = new Date(currMonth.getFullYear(), currMonth.getMonth() + 1, 0, 23, 59, 59);

    const currMonthActivities = mockActivities.filter(activity => {
      const date = new Date(activity.startedAt);
      return date >= startOfMonth && date <= endOfMonth;
    });

    if (currMonthActivities.length === 0) {
      return (
        <div>
          <h2>Insights</h2>
          <p>No activity data available.</p>
        </div>
      );
    }

    const activitiesperDay: Record<string, number>={};
    const caloriesperDay: Record<string, number> = {};

    let mostIntenseActivity = mockActivities[0];
    let totalHeartRate = 0;
    let heartrateCount = 0;

    for (const activity of currMonthActivities) {
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
    let mostActivities = 0;

    for (const day in activitiesperDay) {
        if (activitiesperDay[day]> mostActivities) {
            mostActivities = activitiesperDay[day];
            mostActiveDay = day;
        }
    }

    let leastActiveDay = '';
    let leastActivities = Infinity;

    for (const day in activitiesperDay) {
      if (activitiesperDay[day] < leastActivities) {
        leastActivities = activitiesperDay[day];
        leastActiveDay = day;
      }
    }

    let highestCalorieDay = '';
    let highestCalories = 0;

    for (const day in caloriesperDay) {
        if (caloriesperDay[day]> highestCalories) {
            highestCalories = caloriesperDay[day];
            highestCalorieDay = day;
        }
    }

    let monthlyCalories = 0;
    let monthlySteps = 0;

    for (const activity of currMonthActivities) {
      monthlyCalories += activity.summary.calories || 0;
      monthlySteps += activity.summary.steps || 0;
    }

    // Monthly comparison logic
    const now = new Date();
    let thisMonthCalories = 0;
    let lastMonthCalories = 0;

    for (const activity of currMonthActivities) {
      const date = new Date(activity.startedAt);
      const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

      if (diffDays <= 7) {
        thisMonthCalories += activity.summary.calories || 0;
      } else if (diffDays <= 14) {
        lastMonthCalories += activity.summary.calories || 0;
      }
    }

    let calorieChange = 0;

    if (lastMonthCalories > 0) {
      calorieChange = Math.round(
        ((thisMonthCalories - lastMonthCalories) / lastMonthCalories) * 100
      );
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
                    <p><strong>Most active day:</strong> {mostActiveDay} ({mostActivities} activities)</p>
                    <p><strong>Least active day:</strong> {leastActiveDay} ({leastActivities} activities)</p>
                    <p><strong>Highest calories in one day:</strong> {highestCalorieDay} ({highestCalories} calories)</p>
                    <p><strong>Most intense activity:</strong> {mostIntenseActivity.title} ({mostIntenseActivity.activityType}) -{' '}
                     {mostIntenseActivity.summary.calories || 0} calories</p>
                    <p><strong>Average heart rate:</strong> {averageHeartRate} bpm</p>
                    <p><strong>Total calories:</strong> {monthlyCalories} kcal</p>
                    <p><strong>Total steps:</strong> {monthlySteps}</p>
                    <p>
                      <strong>Monthly trend:</strong>{' '}
                      {calorieChange >= 0
                        ? `+${calorieChange}% more calories than last month 📈`
                        : `${calorieChange}% fewer calories than last month 📉`}
                    </p>
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