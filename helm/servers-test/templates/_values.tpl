{{- define "chart.name" -}}
{{-   .Chart.Name -}}
{{- end -}}

{{- define "chart.appname" -}}
{{- .Release.Name | trunc 53 | trimSuffix "-" -}}
{{- end -}}

{{- define "chart.image.server" -}}
{{-   .Values.image.server -}}
{{- end -}}
