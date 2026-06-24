{{/*
Expand the name of the chart.
*/}}
{{- define "presidio.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "presidio.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "presidio.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified name for a single component (e.g. "<release>-presidio-analyzer").
Call with a dict: (dict "root" $ "name" "analyzer").
*/}}
{{- define "presidio.componentFullname" -}}
{{- printf "%s-%s" (include "presidio.fullname" .root) .name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels.
Call with a dict: (dict "root" $ "name" "analyzer").
*/}}
{{- define "presidio.labels" -}}
helm.sh/chart: {{ include "presidio.chart" .root }}
{{ include "presidio.selectorLabels" . }}
{{- if .root.Chart.AppVersion }}
app.kubernetes.io/version: {{ .root.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .root.Release.Service }}
app.kubernetes.io/part-of: presidio
{{- end }}

{{/*
Selector labels. The component label distinguishes the per-service workloads.
Call with a dict: (dict "root" $ "name" "analyzer").
*/}}
{{- define "presidio.selectorLabels" -}}
app.kubernetes.io/name: {{ include "presidio.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .name }}
{{- end }}

{{/*
Create the name of the service account to use.
*/}}
{{- define "presidio.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "presidio.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Resolve the container image reference for a component.
Call with a dict: (dict "root" $ "component" .Values.analyzer).
registry and pullPolicy fall back to global image.* values; tag falls back to chart appVersion.
*/}}
{{- define "presidio.image" -}}
{{- $registry := .component.image.registry | default .root.Values.image.registry -}}
{{- $tag := .component.image.tag | default .root.Values.image.tag | default .root.Chart.AppVersion -}}
{{- if $registry -}}
{{- printf "%s/%s:%s" $registry .component.image.repository $tag -}}
{{- else -}}
{{- printf "%s:%s" .component.image.repository $tag -}}
{{- end -}}
{{- end }}

{{/*
Deployment template shared by all components.
Call with a dict: (dict "root" $ "name" "analyzer" "component" .Values.analyzer).
*/}}
{{- define "presidio.deployment" -}}
{{- $root := .root -}}
{{- $name := .name -}}
{{- $c := .component -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "presidio.componentFullname" (dict "root" $root "name" $name) }}
  labels:
    {{- include "presidio.labels" (dict "root" $root "name" $name) | nindent 4 }}
spec:
  {{- if not $c.autoscaling.enabled }}
  replicas: {{ $c.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "presidio.selectorLabels" (dict "root" $root "name" $name) | nindent 6 }}
  template:
    metadata:
      annotations:
        {{- with $root.Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
        {{- with $c.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "presidio.labels" (dict "root" $root "name" $name) | nindent 8 }}
        {{- with $root.Values.podLabels }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
    spec:
      {{- with $root.Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "presidio.serviceAccountName" $root }}
      {{- with $root.Values.podSecurityContext }}
      securityContext:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
        - name: {{ $name }}
          {{- with $root.Values.securityContext }}
          securityContext:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          image: {{ include "presidio.image" (dict "root" $root "component" $c) | quote }}
          imagePullPolicy: {{ $c.image.pullPolicy | default $root.Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ $c.containerPort }}
              protocol: TCP
          env:
            - name: PORT
              value: {{ $c.containerPort | quote }}
            - name: WORKERS
              value: {{ $c.workers | quote }}
            {{- with $c.extraEnv }}
            {{- toYaml . | nindent 12 }}
            {{- end }}
          {{- with $c.startupProbe }}
          startupProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with $c.livenessProbe }}
          livenessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with $c.readinessProbe }}
          readinessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with $c.resources }}
          resources:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with $c.volumeMounts }}
          volumeMounts:
            {{- toYaml . | nindent 12 }}
          {{- end }}
      {{- with $c.volumes }}
      volumes:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with ($c.nodeSelector | default $root.Values.nodeSelector) }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with ($c.affinity | default $root.Values.affinity) }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with ($c.tolerations | default $root.Values.tolerations) }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
{{- end }}

{{/*
Service template shared by all components.
Call with a dict: (dict "root" $ "name" "analyzer" "component" .Values.analyzer).
*/}}
{{- define "presidio.service" -}}
{{- $root := .root -}}
{{- $name := .name -}}
{{- $c := .component -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "presidio.componentFullname" (dict "root" $root "name" $name) }}
  labels:
    {{- include "presidio.labels" (dict "root" $root "name" $name) | nindent 4 }}
  {{- with $c.service.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  type: {{ $c.service.type }}
  ports:
    - port: {{ $c.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "presidio.selectorLabels" (dict "root" $root "name" $name) | nindent 4 }}
{{- end }}

{{/*
HorizontalPodAutoscaler template shared by all components.
Call with a dict: (dict "root" $ "name" "analyzer" "component" .Values.analyzer).
*/}}
{{- define "presidio.hpa" -}}
{{- $root := .root -}}
{{- $name := .name -}}
{{- $c := .component -}}
{{- if $c.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "presidio.componentFullname" (dict "root" $root "name" $name) }}
  labels:
    {{- include "presidio.labels" (dict "root" $root "name" $name) | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "presidio.componentFullname" (dict "root" $root "name" $name) }}
  minReplicas: {{ $c.autoscaling.minReplicas }}
  maxReplicas: {{ $c.autoscaling.maxReplicas }}
  metrics:
    {{- if $c.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ $c.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if $c.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ $c.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
{{- end }}
