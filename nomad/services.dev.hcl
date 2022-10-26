variable "volumes_basepath" {
  type        = string
  description = "Base path for mount volumes."
}

job "saksa_dev" {
  datacenters = ["dc1"]
  type        = "service"

  group "services" {
    network {
      port "kafka" {
        to = 9093
        static = 9093
      }
      port "connect_rest" {
        to = 8083
        static = 28083
      }
      port "scylladb" {
        to = 9042
        static = 9042
      }
    }

    task "zookeeper" {
      driver = "docker"

      env {
        ALLOW_ANONYMOUS_LOGIN = "yes"
      }

      config {
        image = "zookeeper:3.7"
        hostname = "zookeeper"
        network_mode = "saksa_nomad_default"
        network_aliases = ["zookeeper"]
        volumes = [
          "${var.volumes_basepath}/saksa_zookeeper-datalog/_data:/datalog",
          "${var.volumes_basepath}/saksa_zookeeper-data/_data:/data"
        ]
      }

      resources {
        cpu    = 500
        memory = 512
      }
    }

    task "kafka" {
      driver = "docker"

      env {
        KAFKA_BROKER_ID = "1"
        KAFKA_CFG_ZOOKEEPER_CONNECT = "zookeeper:2181"
        ALLOW_PLAINTEXT_LISTENER = "yes"
        KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP = "CLIENT:PLAINTEXT,EXTERNAL:PLAINTEXT"
        KAFKA_CFG_LISTENERS = "CLIENT://:9092,EXTERNAL://:9093"
        KAFKA_CFG_ADVERTISED_LISTENERS = "CLIENT://kafka:9092,EXTERNAL://localhost:9093"
        KAFKA_CFG_INTER_BROKER_LISTENER_NAME = "CLIENT"
      }

      config {
        image = "bitnami/kafka"
        network_mode = "saksa_nomad_default"
        network_aliases = ["kafka"]
        ports = ["kafka"]
        volumes = [
          "${var.volumes_basepath}/saksa_kafka-data/_data:/bitnami/kafka"
        ]
      }

      resources {
        cpu    = 500
        memory = 1024
      }
    }

    task "scylladb" {
      driver = "docker"

      config {
        image = "scylladb/scylla:5.1"
        args = [
          "--developer-mode=1"
        ]
        hostname = "scylladb"
        network_mode = "saksa_nomad_default"
        network_aliases = ["scylladb"]
        ports = ["scylladb"]
        volumes = [
          "${var.volumes_basepath}/saksa_scylladb/_data:/var/lib/scylla"
        ]
      }

      resources {
        cpu    = 1000
        memory = 1536
      }
    }

    task "kafka_connect" {
      driver = "docker"

      artifact {
        source = "http://localhost:1234/saksa-connect.tar"
        options {
          archive = false
        }
      }

      lifecycle {
        hook = "poststart"
        sidecar = true
      }

      config {
        load = "saksa-connect.tar"
        image = "saksa-connect"
        network_mode = "saksa_nomad_default"
        network_aliases = ["saksa_connect"]
        ports = ["connect_rest"]
      }

      env {
        GROUP_ID = "1"
        CONFIG_STORAGE_TOPIC = "my-connect-configs"
        OFFSET_STORAGE_TOPIC = "my-connect-offsets"
        BOOTSTRAP_SERVERS = "kafka:9092"
      }

      resources {
        cpu    = 1000
        memory = 1536
      }
    }
  }
}
