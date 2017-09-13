clear all;

%% Settings
% Define system
%A = [0.8 0.1; 0 0.9];
%C = [1 0];
%Q = [1 0; 0 1];
%R = 0.1^2;

% T = 0.01;
% A = [1 T T^2/2; 0 1 T; 0 0 1];
% Q = [T^3/6 T^2/2 T];
% Q = 0.01 * Q' * Q;
% C = [1 0 0];
% R = 0.01^2;

A = [1 0.1; 0 1];
Q = 1^2 * eye(2);
C = [1 0];
R = 1;

noObservations = 1000;
initialState = [0 0];
initialCovariance = 1;

input = zeros([2 noObservations]);
tt = 1:noObservations;
input(1, :) = sin(4 * pi * tt /  noObservations);

dimState = 2;
dimObservation = 1;

%% Data generation
% Simulate the system
state = zeros([dimState, noObservations]);
observation = zeros([dimObservation, noObservations]);

state(:, 1) = initialState;
observation(:, 1) = C * state(:, 1) + mvnrnd(zeros([1, dimObservation]), R)';
for t = 2:noObservations
    state(:, t) = A * state(:, t-1) + input(:, t) + mvnrnd(zeros([1, dimState]), Q)';
    observation(:, t) = C * state(:, t)   + mvnrnd(zeros([1 dimObservation]), R)';
end

%% Kalman filter
% Pre-allocate matrices
predictedStateEstimate = zeros([dimState, noObservations]);
filteredStateEstimate = zeros([dimState, noObservations]);
predictedStateCovariance = zeros([dimState, dimState, noObservations]);
filteredStateCovariance = zeros([dimState, dimState, noObservations]);

% Set initial state and covariance
filteredStateEstimate(:, 1) = initialState;
filteredStateCovariance(:, :, 1) = eye(dimState) * initialCovariance;

for t = 2:noObservations
    %-----------------------------------------------------------------
    % Prediction
    %-----------------------------------------------------------------

    % Propagate state using model
    predictedStateEstimate(:, t) = A * filteredStateEstimate(:, t-1) + input(:, t);

    % Compute the prediction covariance
    predictedStateCovariance(:, :, t) = A * filteredStateCovariance(:, :, t-1) * A' + Q;

    %-----------------------------------------------------------------
    % Correction
    %-----------------------------------------------------------------

    % Compute the innovation and its covariance
    innovation = observation(:, t) - C * predictedStateEstimate(:, t);
    S = C * predictedStateCovariance(:, :, t) * C' + R;

    % Compute the Kalman gain
    kalmanGain = predictedStateCovariance(:, :, t) * C' / S;

    % Correct the estimate and compute filtering covariance
    filteredStateEstimate(:, t) = predictedStateEstimate(:, t) + kalmanGain * innovation;
    filteredStateCovariance(:, :, t) = predictedStateCovariance(:, :, t) - kalmanGain * C * predictedStateCovariance(:, :, t);
end

%% Plotting
figure(1);
subplot(2, 1, 1);
plot(observation); 
xlabel("time");
ylabel("observations");

subplot(2, 1, 2);
plot(1:noObservations, state, 1:noObservations, filteredStateEstimate);
xlabel("time");
ylabel("state");


